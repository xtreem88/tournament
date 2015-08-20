#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect(database_name="tournament"):
    try:
        db = psycopg2.connect("dbname={0}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("Error connecting to database")


def deleteMatches():
    """Remove all the match records from the database."""
    execute_query(['DELETE FROM matches'])


def deletePlayers():
    """Remove all the player records from the database."""
    execute_query(['DELETE FROM players'])


def deleteTournaments():
    """Remove all the tournament records from the database."""
    execute_query(['DELETE FROM tournaments'])


def deleteScorecard():
    """Remove all the scorecard records from the database."""
    execute_query(['DELETE FROM scorecard'])


def countPlayers(t_id):
    """Returns the number of players currently registered.

        Args:
        t_id: id of tournament
    """
    row = execute_find('SELECT count(player) AS num\
             FROM scorecard\
             WHERE tournament = %s', (bleach.clean(t_id),), 1)

    return row[0]


def createTournament(name):
    """Adds a tournament to the database.
    Args:
        Name of tournament

    """
    t_id = execute_query(['INSERT INTO tournaments (name)\
        VALUES (%s) RETURNING id'],
                         [(bleach.clean(name),)], 1)

    return t_id[0]


def registerPlayer(name, t_id):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
      t_id: id of tournament.
    """
    p_id = execute_query(['INSERT INTO players\
        (name) VALUES (%s) RETURNING id'],
                         [(bleach.clean(name),)], 1)

    execute_query(['INSERT INTO scorecard\
        (tournament,player,score,played,bye)\
        VALUES (%s,%s,%s,%s,%s)'],
                  [(bleach.clean(t_id), p_id[0], 0, 0, 0)])


def playerStandings(t_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player
    tied for first place if there is currently a tie.

    Args:
        t_id: id of tournament getting standings for

    Returns:
      A list of tuples, each of which contains (id, name, wins, played):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        played: the number of matches the player has played
    """

    rows = execute_find('SELECT s.player, p.name, s.score, s.played, s.bye\
                 FROM scorecard AS s\
                 INNER JOIN players AS p on p.id = s.player\
                 WHERE tournament = %s\
                 ORDER BY s.score DESC,\
                 s.played DESC', (bleach.clean(t_id),))

    return rows


def hasBye(id, t_id):
    """Checks if player has bye.
    Args:
        id: id of player to check
        t_id: id of tournament
    Returns true or false.
    """
    query = 'SELECT bye FROM scorecard\
             WHERE player = %s AND tournament = %s'
    bye = execute_find(query, (id, t_id), 1)

    if bye[0] == 0:
        return True
    else:
        return False


def reportBye(player, t_id):
    """Assign points for a bye.
    Args:
      player: id of player who receives a bye.
      t_id: the id of the tournament
    """
    query = 'UPDATE scorecard SET score = score+3,\
    bye=bye+1 WHERE player = %s AND tournament = %s'
    execute_query([query], [(player, t_id)])


def checkByes(t_id, ranks, index):
    """Checks if players already have a bye
    Args:
        t_id: tournament id
        ranks: list of current ranks from swissPairings()
        index: index to check
    Returns first id that is valid or original id if none are found.
    """
    if abs(index) > len(ranks):
        return -1
    elif not hasBye(ranks[index][0], t_id):
        return index
    else:
        return checkByes(t_id, ranks, (index - 1))


def reportMatch(t_id, winner, loser, draw='FALSE'):
    """Records the outcome of a single match between two players.
    Args:
      t_id: the id of the tournament match was in
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw:  if the match was a draw
    """
    if draw == 'TRUE':
        win = 1
        loss = 1
    else:
        win = 3
        loss = 0
    insert = 'INSERT INTO matches\
    (tournament, winner, loser, draw)\
    VALUES (%s,%s,%s,%s)'

    win_update = 'UPDATE scorecard SET score = score+%s,\
    played = played+1 WHERE player = %s AND tournament = %s'

    lose_update = 'UPDATE scorecard SET score = score+%s,\
    played = played+1 WHERE player = %s AND tournament = %s'

    execute_query([insert, win_update, lose_update],
                  [(bleach.clean(t_id), bleach.clean(winner),
                    bleach.clean(loser), bleach.clean(draw)),
                   (win, bleach.clean(winner), bleach.clean(t_id)),
                   (loss, bleach.clean(loser), bleach.clean(t_id))
                   ])


def validatePair(player1, player2, t_id):
    """Checks if two players have already played against each other
    Args:
        player1: the id number of first player to check
        player2: the id number of potentail paired player
        t_id: the id of the tournament
    Return true if valid pair, false if not
    """
    query = 'SELECT COUNT(winner) as pair FROM matches\
             WHERE ((winner = %s AND loser = %s)\
                    OR (winner = %s AND loser = %s))\
             AND tournament = %s'
    pairs = execute_find(query, (player1, player2, player2, player1, t_id), 1)

    if pairs[0] > 0:
        return False
    return True


def checkPairs(t_id, ranks, id1, id2):
    """Checks if two players have already had a match against each other.
    If they have, recursively checks through the list until a valid match is
    found.
    Args:
        t_id: id of tournament
        ranks: list of current ranks from swissPairings()
        id1: player needing a match
        id2: potential matched player
    Returns id of matched player or original match if none are found.
    """
    if id2 >= len(ranks):
        return id1 + 1
    elif validatePair(ranks[id1][0], ranks[id2][0], t_id):
        return id2
    else:
        return checkPairs(t_id, ranks, id1, (id2 + 1))


def swissPairings(t_id):
    """Returns a list of pairs of players for the next round of a match.
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
    Args:
        t_id: id of tournament you are gettings standings for
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    ranks = playerStandings(t_id)
    pairs = []

    numPlayers = countPlayers(t_id)
    if numPlayers % 2 != 0:
        bye = ranks.pop(checkByes(t_id, ranks, -1))
        reportBye(t_id, bye[0])

    while len(ranks) > 1:
        validMatch = checkPairs(t_id, ranks, 0, 1)
        player1 = ranks.pop(0)
        player2 = ranks.pop(validMatch - 1)
        pairs.append((player1[0], player1[1], player2[0], player2[1]))

    return pairs


def execute_query(query_list, param_list=None, return_value=0):
    """
    Executes queries with psycopg2

    Args
        query_list: a list of queries to be executed in a transaction
        param_list: list or query parameters arranged with the
                    same index as the queries
        return_value: set to 1 to return a value eg id

    Returns
        The inserted id if the return_valueis set

    """
    db, c = connect()
    id = []
    i = 0
    for query in query_list:
        if param_list is None:
            c.execute(query)
        else:
            c.execute(query, param_list[i])
        if return_value == 1:
            id.append(c.fetchone()[0])
        i += 1
    db.commit()
    db.close()
    if return_value == 1:
        return id


def execute_find(query_string, param_list=None, fetch_one=0):
    """
    Executes select queries with psycopg2

    Args
        query_string: query to be executed
        param_list: list or query parameters
        fetch_one: set to 1 to return only one row

    Returns
        the query result in a list

    """
    db, c = connect()
    if param_list is None:
        c.execute(query_string)
    else:
        c.execute(query_string, param_list)
    if fetch_one == 1:
        rows = c.fetchone()
    else:
        rows = c.fetchall()
    db.close()
    return rows
