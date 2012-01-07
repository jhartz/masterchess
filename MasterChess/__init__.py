"""
MasterChess library
Copyright (C) 2012 Jake Hartz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Usage:
    Import MasterChess and call open_database to get a mc ("MasterChess") instance

Requires Python >= 2.5 and < 3
"""

"""
"outcome" values for matches:
0 - white win
1 - black win
2 - stalemate
3 - draw
"""

import sys, sqlite3

from mc import mc


__author__ = "Jake Hartz"
__copyright__ = "Copyright (C) 2012 Jake Hartz"
__license__ = "GPL"
__version__ = "1.0"


def open_database(path):
    """Check and set up database based on "path", then return an mc ("MasterChess") instance."""
    try:
        conn = sqlite3.connect(path)
        if conn:
            players = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players';")
            if len(players.fetchall()) == 0:
                conn.execute("CREATE TABLE 'players' (id INTEGER PRIMARY KEY, deleted INTEGER, first_name TEXT, last_name TEXT, grade INTEGER);")
            
            matches = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches';")
            if len(matches.fetchall()) == 0:
                conn.execute("CREATE TABLE 'matches' (id INTEGER PRIMARY KEY, enabled INTEGER, timestamp INTEGER, white_player INTEGER, black_player INTEGER, outcome INTEGER);")
            
            prefs = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prefs';")
            if len(prefs.fetchall()) == 0:
                conn.execute("CREATE TABLE 'prefs' (name TEXT UNIQUE NOT NULL, value TEXT);")
            
            conn.commit()
            conn.close()
            mc_instance = mc(path)
            if mc_instance:
                return mc_instance
            else:
                print >> sys.stderr, "open_database WARNING:", "No mc; received:", mc_instance
    except:
        exc_type, exc_value = sys.exc_info()[:2]
        print >> sys.stderr, "open_database ERROR:", exc_type, exc_value