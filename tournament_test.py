#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    c = countPlayers(tid)
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Chandra Nalaar", tid)
    c = countPlayers(tid)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Markov Chaney", tid)
    registerPlayer("Joe Malik", tid)
    registerPlayer("Mao Tsu-hsi", tid)
    registerPlayer("Atlanta Hope", tid)
    c = countPlayers(tid)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deleteScorecard()
    c = countPlayers(tid)
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Melpomene Murray", tid)
    registerPlayer("Randy Schwartz", tid)
    standings = playerStandings(tid)
    if len(standings) < 2:
        raise ValueError("Players should appear in\
            playerStandings even before"
                         " they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 5:
        raise ValueError("Each playerStandings row should have five columns.")
    [(id1, name1, wins1, matches1, bye1),
     (id2, name2, wins2, matches2, bye2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0 or bye1 != 0 or bye2 != 0:
        raise ValueError(
            "Newly registered players should have no matches, wins, or byes.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should\
         appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear\
     in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Bruno Walton", tid)
    registerPlayer("Boots O'Neal", tid)
    registerPlayer("Cathy Burton", tid)
    registerPlayer("Diane Grant", tid)
    standings = playerStandings(tid)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tid, id1, id2)
    reportMatch(tid, id3, id4, 'TRUE')
    standings = playerStandings(tid)
    for (i, n, s, m, b) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i == id1 and s != 3:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id3, id4) and s != 1:
            raise ValueError(
                "Each draw match player should have one point recorded.")
        elif i == id2 and s != 0:
            raise ValueError(
                "Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testReportBye():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Bruno Walton", tid)
    standings = playerStandings(tid)
    id = standings[0][0]
    reportBye(id, tid)
    standings = playerStandings(tid)
    for row in standings:
        if row[4] != 1:
            raise ValueError("This player should have a bye")
    print "8. Byes are reported properly"


def testHasBye():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Bruno Walton", tid)
    standings = playerStandings(tid)
    id = standings[0][0]
    reportBye(id, tid)
    if not hasBye(id, tid):
        raise ValueError("This player should have a bye")
    print "9. Byes are checked properly"


def testCheckByes():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Bruno Walton", tid)
    registerPlayer("Boots O'Neal", tid)
    standings = playerStandings(tid)
    id = standings[-1][0]
    reportBye(id, tid)
    standings = playerStandings(tid)
    test = checkByes(tid, standings, -1)
    if test == -1:
        raise ValueError("This player already has a bye")
    print "10. Byes are assigned properly"


def testPairings():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Twilight Sparkle", tid)
    registerPlayer("Fluttershy", tid)
    registerPlayer("Applejack", tid)
    registerPlayer("Pinkie Pie", tid)
    standings = playerStandings(tid)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tid, id1, id2)
    reportMatch(tid, id3, id4)
    pairings = swissPairings(tid)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "11. After one match, players with one win are paired."


def testOddPairings():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("Twilight Sparkle", tid)
    registerPlayer("Fluttershy", tid)
    registerPlayer("Applejack", tid)
    registerPlayer("Pinkie Pie", tid)
    registerPlayer("Bye Bye", tid)
    standings = playerStandings(tid)
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]
    reportMatch(tid, id1, id2)
    reportMatch(tid, id3, id4)
    pairings = swissPairings(tid)
    if len(pairings) != 2:
        raise ValueError(
            "For five players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs and not hasBye(id5, tid):
        raise ValueError(
            "Bye should be given to last standing")
    print "12. With odd number, last player should have bye."


def testRematch():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    deleteScorecard()
    tid = createTournament('Test')
    registerPlayer("One", tid)
    registerPlayer("Two", tid)
    registerPlayer("Three", tid)
    registerPlayer("Four", tid)
    registerPlayer("Five", tid)
    registerPlayer("Six", tid)
    standings = playerStandings(tid)
    [id1, id2, id3, id4, id5, id6] = [row[0] for row in standings]
    reportMatch(tid, id1, id2)
    reportMatch(tid, id3, id4)
    reportMatch(tid, id5, id6)
    reportMatch(tid, id1, id3)
    reportMatch(tid, id5, id2)
    reportMatch(tid, id4, id6)
    pairings = swissPairings(tid)
    if len(pairings) != 3:
        raise ValueError(
            "For six players, swissPairings should return three pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4),
     (pid5, pname5, pid6, pname6)] = pairings
    correct_pairs = set(
        [frozenset([id1, id5]), frozenset([id3, id2]), frozenset([id4, id6])])
    actual_pairs = set(
        [frozenset([pid1, pid2]), frozenset([pid3, pid4]),
         frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "Rematch occurred.")
    print "13. Rematch avoided."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testReportBye()
    testHasBye
    testCheckByes()
    testPairings()
    testOddPairings()
    testRematch()
    print "Success!  All tests pass!"
