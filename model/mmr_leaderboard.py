from model.config import config
from model.db import dbQuery


def queryLeaderboard(start, count, gameLimit, season=0):
    if season == 0:
        results = dbQuery(
            "SELECT * FROM mmr_leaderboard where isBanned=false and gamesThisSeason>=%s ORDER BY elo DESC LIMIT %s, %s",
            (gameLimit, start, count))
    elif isinstance(season, int):
        results = dbQuery(
            f"SELECT * FROM mmr_leaderboard_season_{season} where isBanned=false and gamesThisSeason>=%s ORDER BY elo DESC LIMIT %s, %s",
            (gameLimit, start, count))
    else:
        results = None
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = LeaderboardEntry(None)
        entry.id = result[0]
        entry.elo = result[1]
        entry.isBanned = result[2]
        entry.gamesThisDecay = result[3]
        entry.gamesThisSeason = result[4]
        entry.gamesThisSeasonWon = result[5]
        entry.seasonHigh = result[6]
        entry.gamesTotal = result[7]
        entry.gamesTotalWon = result[8]
        entries.append(entry)
    return entries


def querySeasonHighLeaderboard(start, count, gameLimit):
    results = dbQuery(
        "SELECT * FROM mmr_leaderboard where isBanned=false and gamesThisSeason>=%s ORDER BY seasonHigh DESC LIMIT %s, %s",
        (gameLimit, start, count))
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = LeaderboardEntry(None)
        entry.id = result[0]
        entry.elo = result[1]
        entry.isBanned = result[2]
        entry.gamesThisDecay = result[3]
        entry.gamesThisSeason = result[4]
        entry.gamesThisSeasonWon = result[5]
        entry.seasonHigh = result[6]
        entry.gamesTotal = result[7]
        entry.gamesTotalWon = result[8]
        entries.append(entry)
    return entries


def countLeaderboard(gameLimit, season=0):
    if season == 0:
        results = dbQuery(
            "SELECT COUNT(*) FROM mmr_leaderboard where isBanned=false and gamesThisSeason>=%s ORDER BY elo DESC",
            (gameLimit,))
    elif isinstance(season, int):
        results = dbQuery(
            f"SELECT COUNT(*) FROM mmr_leaderboard_season_{season} where isBanned=false and gamesThisSeason>=%s ORDER BY elo DESC",
            (gameLimit,))
    else:
        results = None
    if results is None or len(results) == 0:
        return 0
    return results[0][0]


class LeaderboardEntry:
    id = 0
    elo = 0
    isBanned = False
    gamesThisDecay = 0
    gamesThisSeason = 0
    gamesThisSeasonWon = 0
    seasonHigh = 0
    gamesTotal = 0
    gamesTotalWon = 0

    def __init__(self, userId, filterBanned=True):
        if userId is None:
            pass
        else:
            self.queryUser(userId, filterBanned)

    def queryUser(self, userId, filterBanned):
        if filterBanned:
            result = dbQuery("SELECT * FROM mmr_leaderboard where id = %s and isBanned = false", (userId,))
        else:
            result = dbQuery("SELECT * FROM mmr_leaderboard where id = %s", (userId,))
        if result is None or len(result) == 0:
            return None
        self.id = result[0][0]
        self.elo = result[0][1]
        self.isBanned = result[0][2]
        self.gamesThisDecay = result[0][3]
        self.gamesThisSeason = result[0][4]
        self.gamesThisSeasonWon = result[0][5]
        self.seasonHigh = result[0][6]
        self.gamesTotal = result[0][7]
        self.gamesTotalWon = result[0][8]

    def insertUser(self):
        dbQuery(
            "INSERT INTO mmr_leaderboard (id, elo, isBanned, gamesThisDecay, gamesThisSeason, gamesThisSeasonWon, seasonHigh, gamesTotal, gamesTotalWon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (self.id, self.elo, self.isBanned, self.gamesThisDecay, self.gamesThisSeason,
             self.gamesThisSeasonWon, self.seasonHigh, self.gamesTotal, self.gamesTotalWon))

    def updateUser(self):
        update_query = """
        UPDATE mmr_leaderboard SET elo = %s, isBanned = %s, gamesThisDecay = %s, gamesThisSeason = %s, gamesThisSeasonWon = %s, seasonHigh = %s, gamesTotal = %s, gamesTotalWon = %s WHERE id = %s
        """
        dbQuery(update_query, (self.elo,
                               self.isBanned, self.gamesThisDecay, self.gamesThisSeason,
                               self.gamesThisSeasonWon, self.seasonHigh, self.gamesTotal, self.gamesTotalWon, self.id),
                True, False)
