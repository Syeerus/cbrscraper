# File: setup.py
# Author: Syeerus
# License: MIT

"""
Setup script
"""


import argparse
import sqlite3
import os.path
import shutil
import time


def get_args():
    """Parses and returns arguments sent to the script"""
    parser = argparse.ArgumentParser(description='Sets up the database.')
    parser.add_argument('filename', help='Filename to use for the database.')
    parser.add_argument('-b', '--backup', help='Backup if file exists.', action='store_true')
    return parser.parse_args()


def setup_database(filename: str):
    """
    Sets up the database
    :param filename: The filename to use
    """
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute('''CREATE TABLE stations (
                   id INTEGER PRIMARY KEY NOT NULL,
                   name TEXT NOT NULL UNIQUE,
                   url TEXT NOT NULL UNIQUE,
                   scraper TEXT NOT NULL,   --Determines which scraper to use
                   utc_offset REAL NOT NULL
              )''')

    c.execute('''CREATE TABLE artists (
                   id INTEGER PRIMARY KEY NOT NULL,
                   name TEXT NOT NULL UNIQUE
              )''')

    c.execute('''CREATE TABLE songs (
                   id INTEGER PRIMARY KEY NOT NULL,
                   artist_id INTEGER NOT NULL,
                   title TEXT NOT NULL,
                   UNIQUE(artist_id, title)
              )''')

    c.execute('''CREATE TABLE playlists (
                  id INTEGER PRIMARY KEY NOT NULL,
                  station_id INTEGER NOT NULL,
                  song_id INTEGER NOT NULL,
                  timestamp INTEGER NOT NULL
              )''')

    c.execute('''INSERT INTO stations(name, url, scraper, utc_offset) VALUES
                   ('New Country 103.5', 'https://player.newcountry1035.com/CKCHFM/history', 'leanstream', -4),
                   ('GIANT 101.9', 'https://player.giant1019.com/CHRKFM/history', 'leanstream', -4.0),
                   ('Cape 94.9', 'http://mbsradio.leanplayer.com/CKPEFM/history', 'leanstream', -4.0),
                   ('cjcb am 1270', 'http://mbsradio.leanplayer.com/CJCBAM/history', 'leanstream', -4.0),
                   ('MAX FM 98.3', 'http://mbsradio.leanplayer.com/CHERFM/history', 'leanstream', -4.0)
              ''')

    conn.commit()
    conn.close()


def main():
    """Main subroutine"""
    args = get_args()
    if os.path.isfile(args.filename):
        if args.backup:
            current_dir = os.path.dirname(args.filename)
            filename = time.strftime('%Y-%m-%d_%I-%M%p_' + os.path.basename(args.filename), time.gmtime())
            shutil.copy(args.filename, os.path.join(current_dir, filename))
        os.unlink(args.filename)

    setup_database(args.filename)


if __name__ == '__main__':
    main()
