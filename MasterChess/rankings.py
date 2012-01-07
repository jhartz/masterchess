from operator import itemgetter

def get_rankings(mc, include_scores):
    allstats = {}
    playerinfo = {}
    for i in mc.get_players():
        allstats[i.id] = i.stats
        playerinfo[i.id] = i
    
    player_scores = {}
    for id, stats in allstats.iteritems():
        score = 0.0
        if stats.total > 0:
            winratio = float(stats.wins) / float(stats.total)
            lossratio = float(stats.losses) / float(stats.total)
            score = round(winratio - lossratio, 3)
        if score not in player_scores:
            player_scores[score] = []
        player_scores[score].append(id)
    
    # If there are 2 or more players with the same score, we should compare the individual people
    for score, players in player_scores.items():
        if len(players) >= 2:
            new_player_list = compare(mc, players, playerinfo)
            if new_player_list != None:
                base_score = score
                for p in new_player_list:
                    base_score += .0001
                    player_scores[score].remove(p)
                    if base_score not in player_scores:
                        player_scores[base_score] = []
                    player_scores[base_score].append(p)
    
    player_list = []
    for score, players in player_scores.iteritems():
        for p in players:
            player_list.append((p, score, playerinfo[p].grade))
    
    # Sort by score, including grade level in consideration if duplicate scores still exist
    player_list = sorted(player_list, key=itemgetter(1, 2), reverse=True)
    
    if include_scores == False:
        return [i[0] for i in player_list]
    else:
        return [(i[0], i[1]) for i in player_list]

def compare(mc, player_list, playerinfo, recursion_level=0):
    """Compare 2 or more players and return a list of the players in ranked order, or None if no further ranking can be done.
    
    Basically, perform magic.
    """
    if len(player_list) < 2:
        return player_list
    elif len(player_list) == 2:
        playerA, playerB = player_list
        verses_stats = mc.get_players([playerA], [playerB])[0].stats
        if verses_stats.wins > verses_stats.losses:
            return [playerA, playerB]
        elif verses_stats.losses > verses_stats.wins:
            return [playerB, playerA]
        else:
            return None
    else:
        player_scores = {}
        for player in player_list:
            verses_stats = mc.get_players([player], player_list)[0].stats
            score = 0.0
            if verses_stats.total > 0:
                winratio = float(verses_stats.wins) / float(verses_stats.total)
                lossratio = float(verses_stats.losses) / float(verses_stats.total)
                score = winratio - lossratio
            if score not in player_scores:
                player_scores[score] = []
            player_scores[score].append(player)
        
        # If there are still 2 or more players with the same score, we compare the individual people
        for score, players in player_scores.items():
            if len(players) == 2:
                ranked_players = compare(mc, players, playerinfo, recursion_level)
                if ranked_players != None:
                    better_player = ranked_players[0]
                    player_scores[score].remove(better_player)
                    if score + .0001 not in player_scores:
                        player_scores[score + .0001] = []
                    player_scores[score + .0001].append(better_player)
            elif len(players) > 2 and recursion_level < 4:
                new_player_list = compare(mc, players, playerinfo, recursion_level + 1)
                if new_player_list != None:
                    base_score = score
                    for p in new_player_list:
                        base_score += .00001
                        player_scores[score].remove(p)
                        if base_score not in player_scores:
                            player_scores[base_score] = []
                        player_scores[base_score].append(p)
        
        if len(player_scores) > 1:
            player_list = []
            for score, players in player_scores.iteritems():
                for p in players:
                    player_list.append((p, score))
            player_list = sorted(player_list, key=itemgetter(1), reverse=True)
            
            return [player_id for player_id, score in player_list]
        else:
            return None