from model.db import dbQuery


def queryTags(start, end):
    results = dbQuery("SELECT mapTag FROM mmr_maps_tags GROUP BY(mapTag) LIMIT %s, %s", (start, end))
    resultsList = []
    if results is None or len(results) == 0:
        return []
    for result in results:
        resultsList.append(result[0].decode())
    return resultsList


def queryMapsByTag(tag, start, count):
    if tag.lower() == "all":
        results = dbQuery("SELECT * FROM mmr_maps LIMIT %s, %s", (start, count))
    else:
        results = dbQuery(
            "SELECT name, author, link, description, mapTag FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE mapTag = %s OR name LIKE %s GROUP BY(name) LIMIT %s, %s",
            (tag, "%" + tag + "%", start, count))
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = MapEntry()
        entry.name = result[0].decode()
        entry.author = result[1].decode()
        entry.link = result[2].decode()
        entry.description = result[3].decode()
        if len(result) >= 5:
            entry.tags = result[4].decode()
        entries.append(entry)
    return entries


def queryMapsByRandomTag(tag):
    if tag.lower() == "all":
        result = dbQuery("SELECT * FROM mmr_maps ORDER BY RAND() LIMIT 1", ())
    else:
        result = dbQuery(
            "SELECT name, author, link, description, mapTag FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE mapTag = %s OR name LIKE %s GROUP BY(name) ORDER BY RAND() LIMIT 1",
            (tag, "%" + tag + "%"))
    if result is None or len(result) == 0:
        return None
    entry = MapEntry()
    entry.name = result[0][0].decode()
    entry.author = result[0][1].decode()
    entry.link = result[0][2].decode()
    entry.description = result[0][3].decode()
    if len(result[0]) >= 5:
        entry.tags = result[0][4].decode()
    return entry


def countMaps(tag):
    if tag == "all":
        results = dbQuery("SELECT COUNT(*) FROM mmr_maps ORDER BY name", ())
    else:
        results = dbQuery(
            "SELECT COUNT(*) FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE mapTag = %s OR name LIKE %s GROUP BY(name)",
            (tag, "%" + tag + "%"))
    if results is None or len(results) == 0:
        return 0
    return results[0][0]


def countTags():
    results = dbQuery("SELECT COUNT(DISTINCT(mapTag)) FROM mmr_maps_tags", ())
    if results is None or len(results) == 0:
        return 0
    return results[0][0]


class MapEntry:
    name = ""
    author = ""
    link = ""
    description = ""
    tags = ""

    def insertMap(self, tags):
        dbQuery(
            "INSERT INTO mmr_maps (name, author, link, description) VALUES (%s, %s, %s, %s)",
            (self.name, self.author, self.link, self.description), True, False)
        for tag in tags.split(","):
            dbQuery(
                "INSERT INTO mmr_maps_tags (mapName, mapTag) VALUES (%s, %s)",
                (self.name, tag), True, False)

    def updateMap(self):
        update_query = """
        UPDATE mmr_maps SET author = %s, link = %s, description = %s, WHERE name = %s
        """
        dbQuery(update_query, (self.author, self.link, self.description,
                               self.name), True, False)

    def deleteMap(self):
        dbQuery("DELETE FROM mmr_maps WHERE name = %s", (self.name,), True, False)
        dbQuery("DELETE FROM mmr_maps_tags WHERE mapName = %s", (self.name,), True, False)
