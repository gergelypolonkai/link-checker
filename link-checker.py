# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

"""Web link checker script by Gergely Polonkai.
"""

import sys
import time

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

import pprint

pp = pprint.PrettyPrinter(indent=4)


def _is_internal(base_parts, link_parts):
    return base_parts.scheme == link_parts.scheme \
        and base_parts.netloc == link_parts.netloc


def _update_link(checked_links, base_parts, link, origin, checked=False, initial=False):
    was_checked = False
    link_parts = urlparse(link)

    if link in checked_links:
        was_checked = checked_links[link]['checked']
        checked_links[link]['checked'] = checked_links[link]['checked'] or checked

        if not initial:
            checked_links[link]['count'] += 1
    else:
        checked_links[link] = {
            'checked': checked,
            'count': 0 if initial else 1,
            'external': not _is_internal(base_parts, link_parts),
            'sources': set(),
        }

    if origin is not None:
        checked_links[link]['sources'].add(origin)

    return was_checked


class ConnectErrorResponse:
    """Fake response class for links we can’t even connect to (connection or SSL errors)
    """

    ok = False


def main(*args):
    # We will store the links already checked here
    checked_links = {}
    start_time = time.time()

    if len(args) < 1:
        print("Usage: %s <url>" % sys.argv[0])

        return 1

    base_url = args[0]
    base_parts = urlparse(base_url)
    _update_link(checked_links, base_parts, base_url, None, initial=True)
    counter = 0

    while len([x for x in checked_links if not checked_links[x]['checked']]) > 0:
        counter += 1
        link_count = len(checked_links)
        percentage = (counter / link_count) * 100
        current_link = [x for x in checked_links if not checked_links[x]['checked']][0]
        current_parts = urlparse(current_link)

        print(f'Checking {current_link} ({counter}/{link_count}, {percentage:.2f}%)')

        _update_link(checked_links, base_parts, current_link, None, checked=True)

        if current_parts.scheme not in ('http', 'https'):
            checked_links[current_link]['uncheckable'] = True

            continue

        try:
            response = requests.get(current_link, allow_redirects=False)
        except requests.exceptions.ConnectionError:
            response = ConnectErrorResponse()

        if response.ok:
            checked_links[current_link]['broken'] = False
            # If we are being redirected, add the redirect link to
            # link_cache. We will check them later
            if response.is_redirect:
                _update_link(checked_links,
                             base_parts,
                             response.headers['location'],
                             current_link,
                             initial=True)
                checked_links[current_link]['redirect'] = True

                continue
            else:
                checked_links[current_link]['redirect'] = False

            # Don’t crawl external pages
            if checked_links[current_link]['external']:
                continue

            soup = BeautifulSoup(response.content)

            for a in soup.find_all('a'):
                link = urljoin(base_url, a.get('href'))

                _update_link(checked_links, base_parts, link, current_link)
        else:
            checked_links[current_link]['broken'] = True

    pp.pprint(checked_links)

    crawl_time = time.time() - start_time
    print(f'Finished crawling in {crawl_time:.0f}s')


if __name__ == '__main__':
    main(*sys.argv[1:])
