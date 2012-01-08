import sqlite3, os, atexit, datetime, time, sys

from rankings import get_rankings

class Struct(dict):
    """A dict that can be accessed like an object."""
    # Some ideas from http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
    
    def __init__(self, obj={}):
        for key, value in obj.iteritems():
            if isinstance(value, dict):
                # Convert from dict to Struct
                obj[key] = Struct(value)
        dict.__init__(self, obj)
    
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            return dict.__setitem__(self, key, Struct(value))
        else:
            return dict.__setitem__(self, key, value)
    
    def __getattr__(self, key):
        return self.__getitem__(key)
    
    def __setattr__(self, key, value):
        return self.__setitem__(key, value)
    
    def __delattr__(self, key):
        return self.__delitem__(key)
    
    def __repr__(self):
        # Slightly prettier than default (object keys aren't put through repr)
        return "{" + ", ".join("%s: %s" % (key, repr(value)) for (key, value) in self.iteritems()) + "}"

class _PrettyList(list):
    """A list with a prettier repr."""
    
    def __repr__(self, indent=1):
        """Show each list item indented on its own line."""
        # We don't have to indent this first bracket - we can assume it was already indented by parent _PrettyList
        returning = "["
        for i in self:
            returning += "\n" + "    " * indent
            if isinstance(i, list):
                returning += _PrettyList.__repr__(_PrettyList(i), indent + 1)
            else:
                returning += repr(i)
        returning += "\n" + "    " * (indent - 1) + "]"
        return returning

class mc(object):
    """MasterChess base class."""
    
    def __init__(self, db_path, out=sys.stdout):
        self.db_path = db_path
        self._db_conn = sqlite3.connect(self.db_path)
        self.isinit = True
        
        atexit.register(self.uninit)
    
    def uninit(self):
        """Close database. (automatically set to call at exit)"""
        if self.isinit:
            try:
                self._db_conn.close()
                self.isinit = False
            except:
                pass
    
    
    def get_pref(self, pref_name):
        result = self._db_conn.execute("SELECT name, value FROM prefs WHERE name=?", (pref_name,)).fetchone()
        if result:
            return result[1]
        else:
            return None
    
    def set_pref(self, pref_name, pref_value):
        result = self.get_pref(pref_name)
        if result != None:
            self._db_conn.execute("UPDATE prefs SET value=? WHERE name=?", (pref_value, pref_name))
        else:
            self._db_conn.execute("INSERT INTO prefs(name, value) VALUES (?, ?);", (pref_name, pref_value))
        self._db_conn.commit()
    
    
    def add_player(self, first_name, last_name, grade=0):
        """Add a new player."""
        self._db_conn.execute("INSERT INTO players(deleted, first_name, last_name, grade) VALUES (0, ?, ?, ?);", (first_name, last_name, grade))
        self._db_conn.commit()
    
    def update_player(self, id, props):
        """Update a player's metadata."""
        columns = [i[0] for i in self._db_conn.execute("SELECT * FROM players").description]
        for name, value in props.iteritems():
            if name in columns:
                self._db_conn.execute("UPDATE players SET " + name + "=? WHERE id=?", (value, id))
        self._db_conn.commit()
    
    def remove_player(self, id):
        """Remove a player from the database."""
        # Just set "deleted" to 1 - so we don't show it in listings, but we can still access it if it is a value in matches
        self._db_conn.execute("UPDATE players SET deleted=1 WHERE id=?", (id,))
        self._db_conn.commit()
    
    
    def add_match(self, white_player, black_player, outcome, timestamp=0):
        """Add a new match."""
        timestamp = timestamp or time.time()
        self._db_conn.execute("INSERT INTO matches(enabled, timestamp, white_player, black_player, outcome) VALUES (1, ?, ?, ?, ?);", (timestamp, white_player, black_player, outcome))
        self._db_conn.commit()
    
    def update_match(self, id, props):
        """Update a match's metadata."""
        columns = [i[0] for i in self._db_conn.execute("SELECT * FROM matches").description]
        for name, value in props.iteritems():
            if name in columns:
                self._db_conn.execute("UPDATE matches SET " + name + "=? WHERE id=?", (value, id))
        self._db_conn.commit()
    
    def remove_match(self, id):
        """Permanenty remove a match from the database."""
        # Permanently delete (unlike remove_player)
        self._db_conn.execute("DELETE FROM matches WHERE id=?", (id,))
        self._db_conn.commit()
    
    
    def get_players(self, ids=[], verses=[]):
        """Get details about players in the database.
        
        Return details about individual players by specifying them in "ids", or get details for all players if "ids" is empty. If "verses" is specified with one or more player IDs, the stats of the players in "ids" will only reflect the games they played against the players in "verses".
        """
        if not isinstance(ids, list):
            if ids:
                ids = [ids]
            else:
                ids = []
        if not isinstance(verses, list):
            if verses:
                verses = [verses]
            else:
                verses = []
        
        items = []
        if len(ids) == 0:
            items = self._db_conn.execute("SELECT id, first_name, last_name, grade FROM players WHERE deleted!=1 ORDER BY last_name, first_name").fetchall()
        else:
            items = []
            for id in ids:
                result = self._db_conn.execute("SELECT id, first_name, last_name, grade FROM players WHERE id=?", (id,)).fetchone()
                if result:
                    items.append(result)
        
        returnitems = []
        for i in items:
            returnitem = {
                "id": i[0],
                "first_name": i[1],
                "last_name": i[2],
                "grade": i[3]
            }
            white_wins = 0
            white_losses = 0
            black_wins = 0
            black_losses = 0
            stalemates = 0
            draws = 0
            total = 0
            
            if len(verses) > 0:
                cur = self._db_conn.execute("SELECT outcome, white_player FROM matches WHERE enabled=1 AND white_player=? AND (" + (" OR ".join("black_player=?" for i in xrange(len(verses)))) + ")", tuple([i[0]] + verses))
            else:
                cur = self._db_conn.execute("SELECT outcome FROM matches WHERE enabled=1 AND white_player=?", (i[0],))
            for match in cur.fetchall():
                total += 1
                if match[0] == 0:
                    # White won
                    white_wins += 1
                elif match[0] == 1:
                    # Black won
                    white_losses += 1
                elif match[0] == 2:
                    # Stalemate
                    stalemates += 1
                else:
                    # Draw
                    draws += 1
            
            if len(verses) > 0:
                cur = self._db_conn.execute("SELECT outcome, white_player FROM matches WHERE enabled=1 AND black_player=? AND (" + (" OR ".join("white_player=?" for i in xrange(len(verses)))) + ")", tuple([i[0]] + verses))
            else:
                cur = self._db_conn.execute("SELECT outcome, white_player FROM matches WHERE enabled=1 AND black_player=?", (i[0],))
            for match in cur.fetchall():
                total += 1
                if match[0] == 0:
                    # White won
                    black_losses += 1
                elif match[0] == 1:
                    # Black won
                    black_wins += 1
                elif match[0] == 2:
                    # Stalemate
                    stalemates += 1
                else:
                    # Draw
                    draws += 1
            returnitem["stats"] = {
                "wins": white_wins + black_wins,
                "white_wins": white_wins,
                "black_wins": black_wins,
                "losses": white_losses + black_losses,
                "white_losses": white_losses,
                "black_losses": black_losses,
                "stalemates": stalemates,
                "draws": draws,
                "total": total
            }
            returnitems.append(Struct(returnitem))
        return _PrettyList(returnitems)
    
    def get_matches(self, ids=[], exclude_disabled=True):
        """Get details for individual matches via their IDs, or get details for all matches if "ids" is empty. If "exclude_disabled" is False, disabled events will be included in results (only applies if "ids" is empty)."""
        if not isinstance(ids, list):
            if ids:
                ids = [ids]
            else:
                ids = []
        
        items = []
        if len(ids) == 0:
            items = self._db_conn.execute("SELECT id, enabled, timestamp, white_player, black_player, outcome FROM matches " + (exclude_disabled and "WHERE enabled=1 " or "") + "ORDER BY timestamp").fetchall()
        else:
            items = []
            for id in ids:
                result = self._db_conn.execute("SELECT id, enabled, timestamp, white_player, black_player, outcome FROM matches WHERE id=?", (id,)).fetchone()
                if result:
                    items.append(result)
        
        returnitems = []
        for i in items:
            returnitem = {
                "id": i[0],
                "enabled": i[1],
                "timestamp": i[2],
                "white_player": i[3],
                "black_player": i[4],
                "outcome": i[5]
            }
            returnitems.append(Struct(returnitem))
        return _PrettyList(returnitems)
    
    def get_rankings(self, include_scores=False):
        """Return a list of players (or a list of tuples (player ID, score) if include_scores==True) in ranked order, where "score" indicates a player's internal score (higher is better)."""
        return get_rankings(self, include_scores)
    
    def get_grand_table(self, ids=[], full_names=True):
        """Return a dict (Struct) containing "rows", "column_headers", and "row_headers", in which "rows" contains all the players and their scores against each of their opponents (represented by a list of rows, in which each row (list item) contains a list of column values for that row)."""
        if not isinstance(ids, list):
            if ids:
                ids = [ids]
            else:
                ids = []
        
        if full_names == "db":
            pref = self.get_pref("last_names")
            if pref:
                if pref == "yes":
                    full_names = False
                else:
                    full_names = True
            else:
                full_names = True
        
        all_players = {}
        all_ids = []
        for i in self.get_players():
            all_ids.append(i.id)
            all_players[i.id] = i
        
        def get_name(id):
            if full_names:
                return all_players[id].first_name + " " + all_players[id].last_name
            else:
                return all_players[id].last_name
        
        if not ids or len(ids) == 0:
            ids = all_ids
        
        rows = []
        column_totals = {}
        for id in ids:
            row = []
            total_score = 0
            for index, player_id in enumerate(all_ids):
                player = all_players[player_id]
                player_data = self.get_players(id, player.id)[0]
                score = player_data.stats.wins + player_data.stats.stalemates * 0.5 + player_data.stats.draws * 0.5
                total_score += score
                if player_data.stats.total > 0:
                    row.append(score)
                else:
                    row.append(None)
                if not index in column_totals:
                    column_totals[index] = 0
                column_totals[index] += score
            row.append(total_score)
            rows.append(row)
        
        if ids != all_ids:
            old_rows = [[j for j in i] for i in rows]
            column_diff = 0
            for index, player_id in enumerate([i for i in all_ids]):
                if player_id not in ids:
                    no_values = True
                    for row in old_rows:
                        if row[index] != None:
                            no_values = False
                    if no_values:
                        all_ids.remove(player_id)
                        del column_totals[index]
                        for row_index, row in enumerate(old_rows):
                            # I see the problem... We're still deleting a certain index from newrows, even though it doesn't really exist
                            del rows[row_index][index - column_diff]
                        column_diff += 1
        
        new_column_totals = sorted([(index, score) for index, score in column_totals.iteritems()])
        rows.append([value for index, value in new_column_totals])
        column_headers = [(id, "vs. " + get_name(id)) for id in all_ids] + ["TOTAL WINS"]
        row_headers = [(id, get_name(id)) for id in ids] + ["TOTAL LOSSES"]
        return Struct({
            "rows": rows,
            "column_headers": column_headers,
            "row_headers": row_headers
        })
    
    def get_stats(self):
        """Return an object/dict containing interesting stats."""
        returning = {}
        
        white = 0
        black = 0
        stalemate = 0
        draw = 0
        total = 0
        matches = self.get_matches()
        for match in matches:
            total += 1
            if match.outcome == 0:
                white += 1
            elif match.outcome == 1:
                black += 1
            elif match.outcome == 2:
                stalemate += 1
            else:
                draw += 1
        returning["totals"] = {
            "white_wins": white,
            "black_wins": black,
            "stalemates": stalemate,
            "draws": draw,
            "matches": total
        }
        if total > 0:
            returning["outcomes"] = {
                "white": float(white) / float(total),
                "black": float(black) / float(total),
                "stalemate": float(stalemate) / float(total),
                "draw": float(draw) / float(total)
            }
        else:
            returning["outcomes"] = {
                "white": 0.0,
                "black": 0.0,
                "stalemate": 0.0,
                "draw": 0.0
            }
        
        return Struct(returning)