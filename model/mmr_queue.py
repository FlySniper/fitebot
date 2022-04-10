import datetime

from model.db import dbQuery


def queryQueue(queueName):
    results = dbQuery(
        "SELECT * FROM mmr_queue where queueName=%s ORDER BY exitDate",
        (queueName,))
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = QueueEntry(None, None)
        entry.id = result[0]
        entry.elo = result[1]
        entry.exitDate = result[2]
        entry.queueName = result[3]
        entries.append(entry)
    return entries


def countQueue():
    results = dbQuery("SELECT COUNT(*) FROM mmr_leaderboard ORDER BY exitDate")
    if results is None or len(results) == 0:
        return []
    return results[0][0]


class QueueEntry:
    id = 0
    elo = 0
    exitDate = datetime.datetime(1900, 1, 1, 0, 0, 0)
    queueName = ""

    def __init__(self, userId, queueName):
        if userId is None or queueName is None:
            pass
        else:
            self.queryUser(userId, queueName)

    def queryUser(self, userId, queueName):
        result = dbQuery("SELECT * FROM mmr_queue where id = %s and queueName = %s", (userId, queueName))
        if result is None or len(result) == 0:
            return None
        self.id = result[0][0]
        self.elo = result[0][1]
        self.exitDate = result[0][2]
        self.queueName = result[0][3]

    def insertUser(self):
        dbQuery(
            "INSERT INTO mmr_queue (id, elo, exitDate, queueName) VALUES (%s, %s, %s, %s)",
            (self.id, self.elo, self.exitDate, self.queueName,), True, False)

    def updateUser(self):
        update_query = """
        UPDATE mmr_queue SET elo = %s, exitDate = %s, queueName = %s WHERE id = %s
        """
        dbQuery(update_query, (self.elo, self.exitDate,
                               self.queueName, self.id), True, False)

    def deleteUser(self):
        dbQuery("DELETE FROM mmr_queue WHERE id = %s and queueName = %s", (self.id, self.queueName.decode()), True, False)
