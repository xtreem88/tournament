#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


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
             WHERE tournament = \'{0}\''.format(bleach.clean(t_id)), 1)
    
    return row[0]

def createTournament(name):
    """Adds a tournament to the database.
    Args:
        Name of tournament

    """
    t_id = execute_query(['INSERT INTO tournaments (name)\
        VALUES (\'{0}\') RETURNING id'.format(bleach.clean(name),)], 1)


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
        (name) VALUES (\'{0}\') RETURNING id'.format(bleach.clean(name),)], 1)
   
    execute_query(['INSERT INTO scorecard\
        (tournament,player,score,played,bye)\
        VALUES (\'{0}\',\'{1}\',\'{2}\',\'{3}\',\'{4}\')'.format(bleach.clean(t_id), p_id[0], 0, 0, 0)])



def playerStandings(t_id):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player
    tied for first place if there is currently a tie.

    Args:
        tid: id of tournament getting standings for

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
                 WHERE tournament = \'{0}\'\
                 ORDER BY s.score DESC, s.played DESC'.format(bleach.clean(t_id)))

    
    return rows


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

    execute_query(['INSERT INTO matches\
    (tournament, winner, loser, draw)\
    VALUES (\'{0}\',\'{1}\',\'{2}\',\'{3}\')\
    '.format(bleach.clean(t_id), bleach.clean(winner), 
        bleach.clean(loser), bleach.clean(draw)),
    'UPDATE scorecard SET score = score+\'{0}\',\
    played = played+1 WHERE player = \'{1}\' AND tournament = \'{2}\'\
    '.format(win, bleach.clean(winner), bleach.clean(t_id)),
        'UPDATE scorecard SET score = score+\'{0}\',\
    played = played+1 WHERE player = \'{1}\' AND tournament = \'{2}\'\
    '.format(win, bleach.clean(loser), bleach.clean(t_id))])


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """


def execute_query(query_list, return_value=0):
    db = connect()
    c = db.cursor()
    id = []
    for query in query_list:
        c.execute(query)
        if return_value == 1:
            id.append(c.fetchone()[0])
    db.commit()
    db.close()
    if return_value == 1:
        return id



def execute_find(query_string, fetch_one=0):
    db = connect()
    c = db.cursor()
    c.execute(query_string)
    if fetch_one == 1:
        rows = c.fetchone()
    else:
        rows = c.fetchall()
    db.close()
    return rows
