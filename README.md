# Link checker

This is a small link checker script intended for checking and listing
all links that can be found on the specified pages, and all other
pages linked from that site.

The script also crawls the site, checking all links on the same
server. External links are checked but not crawled.

A site is considered external if its hostname or even its scheme
(http:// instead of https://) doesn’t match with the base URL
(specified on the command line).
