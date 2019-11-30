# Cape Breton Radio Scraper #

This project is used for scraping music radio stations that are broadcasting around
Cape Breton, Nova Scotia.

## Requirements ##
+ Python 3.6+

## Usage ##
*setup.py*
```
usage: setup.py [-h] [-b] filename

Sets up the database.

positional arguments:
  filename      Filename to use for the database.

optional arguments:
  -h, --help    show this help message and exit
  -b, --backup  Backup if file exists.

```

*cbrscraper/cbrscraper.py*
```
usage: cbrscraper.py [-h] [-c CONNECTION_ATTEMPTS] [-t TIMEOUT] [-b [BACKUP]]
                     [-l {CRITICAL,ERROR,WARNING,INFO,DEBUG}] [-v]
                     filename

Scrapes a play list defined in an SQLite3 database.

positional arguments:
  filename              Filename of the database to use.

optional arguments:
  -h, --help            show this help message and exit
  -c CONNECTION_ATTEMPTS, --connection-attempts CONNECTION_ATTEMPTS
                        How many times to try downloading a playlist.
  -t TIMEOUT, --timeout TIMEOUT
                        Seconds to wait for a connection to succeed.
  -b [BACKUP], --backup [BACKUP]
                        Backs up the file if it exists, with optional path.
  -l {CRITICAL,ERROR,WARNING,INFO,DEBUG}, --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        Set logging level.
  -v, --version         Displays version info.
```
