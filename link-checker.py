# -*- coding: utf-8 -*-
#
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

"""
Web link checker script by Gergely Polonkai.
"""

import sys
from bs4 import BeautifulSoup
import requests
import re
import urlparse

import pprint

pp = pprint.PrettyPrinter(indent=4)

def _is_internal(base_parts, link_parts):
    return base_parts.scheme == link_parts.scheme \
        and base_parts.netloc == link_parts.netloc

def _update_link(checked_links, base_parts, link, checked=False, initial=False):
    was_checked = False
    link_parts = urlparse.urlparse(link)

    if link in checked_links:
        was_checked = checked_links[link]['checked']
        checked_links[link]['checked'] = checked_links[link]['checked'] \
                                         or checked
        if not initial:
            checked_links[link]['count'] += 1
    else:
        checked_links[link] = {
            'checked': checked,
            'count': 0 if initial else 1,
            'external': not _is_internal(base_parts, link_parts),
        }

    return was_checked

def main(*args):
    # We will store the links already checked here
    checked_links = {}

    if len(args) < 1:
        print("Usage: %s <url>" % sys.argv[0])

        return 1

    base_url = args[0]
    base_parts = urlparse.urlparse(base_url)
    _update_link(checked_links, base_parts, base_url, initial=True)

    while len([x for x in checked_links \
               if checked_links[x]['checked'] == False]) > 0:

        current_link = [x for x in checked_links \
                        if checked_links[x]['checked'] == False][0]
        current_parts = urlparse.urlparse(current_link)

        print("Checking %s" % current_link)

        _update_link(checked_links, base_parts, current_link, checked=True)

        checked_links[current_link]['uncheckable'] = current_parts.scheme \
                                                     not in ('http', 'httus',)

        if checked_links[current_link]['uncheckable']:
            continue

        response = requests.get(current_link, allow_redirects=False)

        if response.ok:
            checked_links[current_link]['broken'] = False
            # If we are being redirected, add the redirect link to
            # link_cache. We will check them later
            if response.is_redirect:
                _update_link(
                    checked_links,
                    base_parts,
                    response.headers['location'],
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
                link = urlparse.urljoin(base_url, a.get('href'))
                link_parts = urlparse.urlparse(link)

                _update_link(checked_links, base_parts, link)
        else:
            checked_links[current_link]['broken'] = True

    pp.pprint(checked_links)

if __name__ == '__main__':
    main(*sys.argv[1:])
