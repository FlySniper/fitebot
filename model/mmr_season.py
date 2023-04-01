from model.db import dbQuery


def querySeason():
    results = dbQuery(
        "SELECT * FROM mmr_season", ())
    if results is None or len(results) == 0:
        return 1
    entries = []
    return results[0][0]


def incrementSeason():
    dbQuery("UPDATE mmr_season SET ID = ID + 1", (), True, False)


def backupLeaderboardForNewSeason(seasonNum):
    dbQuery(f"CREATE TABLE mmr_leaderboard_season_{seasonNum} LIKE mmr_leaderboard", (), True, False)
    dbQuery(f"INSERT INTO mmr_leaderboard_season_{seasonNum} SELECT * FROM mmr_leaderboard", (), True, False)
    dbQuery("UPDATE mmr_leaderboard SET gamesThisSeason = 0, gamesThisSeasonWon = 0, seasonHigh = elo", (), True, False)

