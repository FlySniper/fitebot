import datetime

from model.db import dbQuery


class MatchHistoryEntry:
    id = 0
    winner = 0
    winner_elo_old = 0.0
    winner_elo_new = 0.0
    loser = 0
    loser_elo_old = 0.0
    loser_elo_new = 0.0
    undo_expire_date = datetime.datetime(1900, 1, 1, 0, 0, 0)

    def __init__(self, winnerId, loserId):
        if winnerId is None or loserId is None:
            pass
        else:
            self.queryEntry(winnerId, loserId)

    def queryEntry(self, winnerId, loserId):
        result = dbQuery("SELECT * FROM mmr_match_history where winner = %s and loser = %s ORDER BY id DESC",
                         (winnerId, loserId))
        if result is None or len(result) == 0:
            return None
        self.id = result[0][0]
        self.winner = result[0][1]
        self.winner_elo_old = result[0][2]
        self.winner_elo_new = result[0][3]
        self.loser = result[0][4]
        self.loser_elo_old = result[0][5]
        self.loser_elo_new = result[0][6]
        self.undo_expire_date = result[0][7]

    def insertEntry(self):
        dbQuery(
            "INSERT INTO mmr_match_history (id, winner, winner_elo_old, winner_elo_new, loser, loser_elo_old, loser_elo_new, undo_expire_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (self.id, self.winner, self.winner_elo_old, self.winner_elo_new, self.loser, self.loser_elo_old,
             self.loser_elo_new, self.undo_expire_date), True, False)

    def updateEntry(self):
        update_query = """
        UPDATE mmr_match_history SET winner = %s, winner_elo_old = %s, winner_elo_new = %s, loser = %s, loser_elo_old = %s, loser_elo_new = %s, undo_expire_date = %s WHERE id = %s
        """
        dbQuery(update_query, (self.id, self.winner, self.winner_elo_old, self.winner_elo_new, self.loser,
                               self.loser_elo_old, self.loser_elo_new, self.undo_expire_date), True, False)

    def deleteEntry(self):
        dbQuery("DELETE FROM mmr_match_history WHERE id = %s", (self.id,), True, False)
