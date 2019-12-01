#!/usr/bin/env python3
# File: cbrscraper.py
# Author: Syeerus
# License: MIT


import argparse
import json
import os
import time
import shutil
import logging
import sqlite3
import json
import scrapers.leanstream
from urllib.request import URLError
from helpers import str_to_log_level
from exceptions import UnknownScraperError


VERSION = '0.1.0'

HEADERS_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'headers.json')

LOG_FILENAME = 'events.log'

# Max connection attempts
DEFAULT_MAX_CONNECTION_ATTEMPTS = 2

# Default timeout for connections in seconds
DEFAULT_CONNECTION_TIMEOUT = 5


def get_args():
    """
    Parses arguments from the command line
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Scrapes playlists defined in an SQLite3 database.')
    parser.add_argument('filename', help='Filename of the database to use.')
    parser.add_argument('-c', '--connection-attempts', help='How many times to try downloading a playlist.', default=DEFAULT_MAX_CONNECTION_ATTEMPTS)
    parser.add_argument('-t', '--timeout', help='Seconds to wait for a connection to succeed.', default=DEFAULT_CONNECTION_TIMEOUT)
    parser.add_argument('-b', '--backup', nargs='?', help='Backs up the file if it exists, with optional path.', default=False, const=True)
    parser.add_argument('-l', '--log-level', help='Set logging level.', default='ERROR', choices=('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG',))
    parser.add_argument('-v', '--version', help='Displays version info.', action='version', version='v{0}'.format(VERSION))
    return parser.parse_args()


def backup_old_file(filename: str, backup):
    """
    Backs up the old database file
    :param filename: File to backup
    :param backup: Flag for backup to default location or path for the backup location
    :raises: FileNotFoundError,
    """
    if os.path.isfile(filename):
        if backup:
            copy_filename = time.strftime('%Y-%m-%d_%I-%M%p_' + os.path.basename(filename), time.gmtime())
            if type(backup) == str:
                if not os.path.isdir(backup):
                    os.makedirs(backup)
                copy_filename = os.path.join(backup, copy_filename)
            shutil.copy(filename, copy_filename)
    else:
        raise FileNotFoundError("Filename '{0}' not found".format(filename))


def get_headers() -> dict:
    """
    Returns headers read from the headers file
    :return: Headers
    """
    try:
        with open(HEADERS_FILE, 'r', encoding='utf-8') as f:
            data = f.read()
        data = json.loads(data, encoding='utf-8')
        if type(data) != dict:
            raise Exception('JSON data is not an object.')
        return data
    except Exception as e:
        logger = logging.getLogger('cbrscraper')
        logger.warning(e)
        return {}


def populate_ids(ids: dict, artists: list, songs: list):
    """
    Populates a dictionary with artist and song IDs
    :param ids: Dictionary to store the data
    :param artists: List of artist rows
    :param songs: List of song rows
    """
    for i in range(0, len(artists)):
        ids['artists'][artists[i]['name']] = artists[i]['id']

    for i in range(0, len(songs)):
        key = songs[i]['artist_id']
        if not key in ids['artists_songs']:
            ids['artists_songs'][key] = {}
        ids['artists_songs'][key][songs[i]['title']] = songs[i]['id']


def prepare_data(song: dict) -> dict:
    """
    Prepares song dataa for database insertion to cut down on duplicates
    :param song: Song data
    :return: The song data
    """
    song['artist'] = song['artist'].upper().strip()
    song['title'] = song['title'].upper().strip()
    return song


def scrape_station(cursor: sqlite3.Cursor, station: sqlite3.Row, ids: dict, headers: dict, connection_attempts: int, timeout: int):
    """
    Scrapes a single station
    :param cursor:  SQLite3 cursor
    :param station: Station record
    :param ids: Dictionary of ID associations
    :param headers: HTTP headers to send
    :param connection_attempts: Number of times to try downloading the playlist
    :param timeout: Seconds to wait for a successful connection
    :raises: UnknownScraperError
    """
    query = cursor.execute('SELECT * FROM playlists WHERE station_id=? ORDER BY timestamp DESC LIMIT 1', (station['id'],))
    last_row = query.fetchone()
    scraper = None
    if station['scraper'] == 'leanstream':
        scraper = scrapers.leanstream.LeanStreamScraper(station['url'], timeout, headers, float(station['utc_offset']))
    else:
        raise UnknownScraperError("Scraper '{0}' is unknown.".format(station['scraper']))

    data = []
    logger = logging.getLogger('cbrscraper')
    logger.info("Scraping station '{0}'".format(station['name']))
    for i in range(0, connection_attempts):
        logger.info('Connection attempt #{0}'.format(i + 1))
        try:
            data = scraper.scrape()
            break
        except URLError as e:
            logger.warning("Could not download playlist from '{0}' - Attempt #{1}".format(scraper.url, i + 1))
            if i == (connection_attempts - 1):
                logger.error('Max connection attempts reached.')
        except Exception as e:
            logger.error("An error occured for station '{0}' - {1}".format(station['name'], e))

    for i in range(0, len(data)):
        song = prepare_data(data[i])
        artist_id = None
        song_id = None
        if song['artist'] in ids['artists']:
            artist_id = ids['artists'][song['artist']]
        else:
            cursor.execute('INSERT INTO artists(name) VALUES(?)', (song['artist'],))
            artist_id = cursor.lastrowid
            ids['artists'][song['artist']] = artist_id
            ids['artists_songs'][artist_id] = {}

        if song['title'] in ids['artists_songs'][artist_id]:
            song_id = ids['artists_songs'][artist_id][song['title']]
        else:
            cursor.execute('INSERT INTO songs(artist_id, title) VALUES(?, ?)', (artist_id, song['title'],))
            song_id = cursor.lastrowid
            ids['artists_songs'][artist_id][song['title']] = song_id

        if last_row and last_row['song_id'] == song_id and last_row['timestamp'] == song['time']:
            # We're at where we left off last time
            logger.info('Found last row from previous run. {0} - {1}'.format(song['artist'], song['title']))
            break

        cursor.execute('INSERT INTO playlists(station_id, song_id, timestamp) VALUES(?, ?, ?)',
                       (station['id'], song_id, song['time'],))


def scrape(filename: str, connection_attempts: int, timeout: int):
    """
    Scrapes the radio stations
    :param filename: Name of the database file
    :param connection_attempts: Number of attempts to download a playlist
    :param timeout: Seconds to wait for a successful connection
    """
    headers = get_headers()
    conn = sqlite3.connect(filename)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = c.execute('SELECT * FROM stations')
    stations = query.fetchall()
    query = c.execute('SELECT * FROM artists')
    artists = c.fetchall()
    query = c.execute('SELECT * FROM songs')
    songs = c.fetchall()

    # Stored IDs for easy lookup
    ids = {
        'artists': {},           # Name is the key, ID is the value
        'artists_songs': {}      # Artist ID is the key to another dictionary {'%songtitle%': '%songid%'}
    }
    populate_ids(ids, artists, songs)

    for i in range(0, len(stations)):
        scrape_station(c, stations[i], ids, headers, connection_attempts, timeout)

    conn.commit()
    conn.close()


def main():
    """Main subroutine"""
    args = get_args()
    logging.basicConfig(filename=LOG_FILENAME, filemode='a', format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s', \
                        datefmt='%Y-%m-%d %I:%M %p', level=str_to_log_level(args.log_level))
    try:
        backup_old_file(args.filename, args.backup)
        scrape(args.filename, args.connection_attempts, args.timeout)
    except Exception as e:
        print('Error: {0}'.format(e))
        logger = logging.getLogger('cbrscraper')
        logger.error(e)


if __name__ == '__main__':
    main()
