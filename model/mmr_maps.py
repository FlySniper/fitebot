from model.db import dbQuery


def queryMapsByTag(tag, start, count):
    if tag.lower() == "all":
        results = dbQuery("SELECT * FROM mmr_maps LIMIT %s, %s", (start, count))
    else:
        results = dbQuery("SELECT * FROM mmr_maps where tags LIKE %s OR name LIKE %s LIMIT %s, %s", (tag, tag, start, count))
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = MapEntry(None)
        entry.name = result[0].decode()
        entry.author = result[1].decode()
        entry.link = result[2].decode()
        entry.queueNames = result[3].decode()
        entry.description = result[4].decode()
        entry.tags = result[5].decode()
        entries.append(entry)
    return entries


def queryMapsByRandomTag(tag):
    if tag.lower() == "all":
        result = dbQuery("SELECT * FROM mmr_maps ORDER BY RAND() LIMIT 1", ())
    else:
        result = dbQuery("SELECT * FROM mmr_maps where tags LIKE %s OR name LIKE %s ORDER BY RAND() LIMIT 1", (tag, tag))
    if result is None or len(result) == 0:
        return None
    entry = MapEntry(None)
    entry.name = result[0][0].decode()
    entry.author = result[0][1].decode()
    entry.link = result[0][2].decode()
    entry.queueNames = result[0][3].decode()
    entry.description = result[0][4].decode()
    entry.tags = result[0][5].decode()
    return entry

def countMaps():
    results = dbQuery("SELECT COUNT(*) FROM mmr_maps ORDER BY name")
    if results is None or len(results) == 0:
        return []
    return results[0][0]


class MapEntry:
    name = ""
    author = ""
    link = ""
    queueNames = ""
    description = ""
    tags = ""

    def __init__(self, name):
        if name is None or name == "":
            pass
        else:
            self.queryMap(name)

    def queryMap(self, name):
        result = dbQuery("SELECT * FROM mmr_maps where name LIKE %s", (name,))
        if result is None or len(result) == 0:
            return None
        self.name = result[0][0]
        self.author = result[0][1]
        self.link = result[0][2]
        self.queueNames = result[0][3]
        self.description = result[0][4]
        self.tags = result[0][5]

    def insertMap(self):
        dbQuery(
            "INSERT INTO mmr_maps (name, author, link, queueNames) VALUES (%s, %s, %s, %s)",
            (self.name, self.author, self.link, self.queueNames,), True, False)

    def updateMap(self):
        update_query = """
        UPDATE mmr_maps SET author = %s, link = %s, queueNames = %s WHERE name = %s
        """
        dbQuery(update_query, (self.author, self.link,
                               self.queueNames, self.name), True, False)

    def deleteMap(self):
        dbQuery("DELETE FROM mmr_maps WHERE name = %s and queueName = %s", (self.name, self.queueNames.decode()), True, False)
