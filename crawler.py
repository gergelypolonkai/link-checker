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

def main(*args):
    # We will store the links already checked here
    checked_links = []

    # This contains the links that still needs to be checked
    link_cache = []

    if len(args) < 1:
        print("Usage: %s <url>" % sys.argv[0])
        return 1

    base_url = args[0]
    link_cache.append(base_url)

    while len(link_cache) > 0:
        link = link_cache[0]
        link_cache = [x for x in link_cache if x != link]
        checked_links.append(link)

        print("Checking %s" % link)

        r = requests.get(link)

        if r.status_code == 200:
            soup = BeautifulSoup(r.content)

            for a in soup.find_all('a'):
                link = urlparse.urljoin(base_url, a.get('href'))

                if link.startswith(base_url):
                    if link not in checked_links:
                        link_cache.append(link)
                    else:
                        print("Skipping checked link %s" % link)
                else:
                    print("Skipping external link %s" % link)
        else:
            print r.status_code

    print("Done. Checked links:")

    with open('link_list.txt', 'w') as f:
        for link in checked_links:
            f.write(link + "\n")
            print link

if __name__ == '__main__':
    main(*sys.argv[1:])
