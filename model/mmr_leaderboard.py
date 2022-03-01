from client import MyClient
from model.db import dbQuery


class LeaderboardEntry:
    id = 0
    elo = 0
    discordTag = "Person#1234"
    isBanned = False
    gamesThisDecay = 0
    gamesThisSeason = 0
    gamesThisSeasonWon = 0
    seasonHigh = 0

    def __init__(self, userId):
        if userId is None:
            pass
        else:
            self.queryUser(userId)

    def queryUser(self, userId):
        result = dbQuery("SELECT * FROM mmr_leaderboard where id='%d'", (userId,))
        if result is None or len(result) != 0:
            return None
        self.id = result[0][0]
        self.elo = result[0][1]
        self.discordTag = result[0][2]
        self.isBanned = result[0][3]
        self.gamesThisDecay = result[0][4]
        self.gamesThisSeason = result[0][5]
        self.gamesThisSeasonWon = result[0][6]
        self.seasonHigh = result[0][7]

    def queryLeaderboard(self):
        gameLimit = MyClient.config["game-limit-count"]
        results = dbQuery("SELECT * FROM mmr_leaderboard where isBanned=false and gamesThisSeason>='%d'",
                          (gameLimit,))
        if results is None or len(results) != 0:
            return []
        entries = []
        for result in results:
            entry = LeaderboardEntry(None)
            entry.id = result[0]
            entry.elo = result[1]
            entry.discordTag = result[2]
            entry.isBanned = result[3]
            entry.gamesThisDecay = result[4]
            entry.gamesThisSeason = result[5]
            entry.gamesThisSeasonWon = result[6]
            entry.seasonHigh = result[7]
            entries.append(entry)
        return entries

    def insertUser(self):
        dbQuery(
            "INSERT INTO mmr_leaderboard (id, elo, discordTag, isBanned, gamesThisDecay, gamesThisSeason, gamesThisSeasonWon, seasonHigh) VALUES (%d, %f, %.128s, %d, %d, %d, %d, %f)",
            (self.id, self.elo, self.discordTag, self.isBanned, self.gamesThisDecay, self.gamesThisSeason,
             self.gamesThisSeasonWon, self.seasonHigh))

    def updateUser(self):
        update_query = """
        UPDATE mmr_leaderboard SET 
        id = %d and elo = %f and discordTag = %.128s and isBanned = %d and 
        gamesThisDecay = %d and gamesThisSeason = %d and gamesThisSeasonWon = %d and seasonHigh = %f 
        WHERE id = '%d'
        """
        dbQuery(update_query, (self.id, self.elo, self.discordTag,
                               self.isBanned, self.gamesThisDecay, self.gamesThisSeason,
                               self.gamesThisSeasonWon, self.seasonHigh, self.id))
