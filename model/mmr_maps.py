import datetime

from model.db import dbQuery


def queryTags(start, end):
    results = dbQuery("SELECT mapTag FROM mmr_maps_tags GROUP BY(mapTag) LIMIT %s, %s", (start, end))
    resultsList = []
    if results is None or len(results) == 0:
        return []
    for result in results:
        resultsList.append(result[0])
    return resultsList


def queryTagsByMapName(name):
    results = dbQuery("SELECT mapTag FROM mmr_maps_tags WHERE mapName = %s GROUP BY(mapTag)",
                      (name,))
    resultsList = []
    if results is None or len(results) == 0:
        return []
    for result in results:
        resultsList.append(result[0])
    return resultsList


def queryMapsByPostId(postId, start, count):
    results = dbQuery("SELECT * FROM mmr_maps WHERE postId = %s LIMIT %s, %s", (postId, start, count))
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = create_map_entry(result)
        entries.append(entry)
    return entries


def queryMapsByTagOrName(tag, start, count):
    if tag.lower() == "all":
        results = dbQuery("SELECT * FROM mmr_maps LIMIT %s, %s", (start, count))
    else:
        results = dbQuery(
            "SELECT name, author, link, website, description, short_description, postId, created_date, updated_date, up_votes, down_votes, mapTag FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE mapTag = %s OR name LIKE %s GROUP BY(name) LIMIT %s, %s",
            (tag, "%" + tag + "%", start, count))
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = create_map_entry(result)
        entries.append(entry)
    return entries


def create_map_entry(result):
    entry = MapEntry()
    entry.name = result[0]
    entry.author = result[1]
    entry.link = result[2]
    entry.website = result[3]
    entry.description = result[4]
    entry.short_description = result[5]
    entry.postId = result[6]
    entry.created_date = result[7]
    entry.updated_date = result[8]
    entry.up_votes = result[9]
    entry.down_votes = result[10]
    if len(result) >= 11:
        entry.tags = ",".join(queryTagsByMapName(entry.name))
    return entry


def queryMapsByTag(tag, start, count):
    if tag.lower() == "all":
        results = dbQuery("SELECT * FROM mmr_maps LIMIT %s, %s", (start, count))
    else:
        results = dbQuery(
            "SELECT name, author, link, website, description, short_description, postId, created_date, updated_date, up_votes, down_votes, mapTag FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE mapTag = %s GROUP BY(name) LIMIT %s, %s",
            (tag, start, count))
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = create_map_entry(result)
        entries.append(entry)
    return entries


def queryMapsByName(tag, start, count):
    if tag.lower() == "all":
        results = dbQuery("SELECT * FROM mmr_maps LIMIT %s, %s", (start, count))
    else:
        results = dbQuery(
            "SELECT name, author, link, website, description, short_description, postId, created_date, updated_date, up_votes, down_votes, mapTag FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE name = %s GROUP BY(name) LIMIT %s, %s",
            (tag, start, count))
    if results is None or len(results) == 0:
        return []
    entries = []
    for result in results:
        entry = create_map_entry(result)
        entries.append(entry)
    return entries


def queryMapsByRandomTagOrName(tag):
    if tag.lower() == "all":
        result = dbQuery("SELECT * FROM mmr_maps ORDER BY RAND() LIMIT 1", ())
    else:
        result = dbQuery(
            "SELECT name, author, link, website, description, short_description, postId, created_date, updated_date, up_votes, down_votes, mapTag FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE mapTag = %s OR name LIKE %s GROUP BY(name) ORDER BY RAND() LIMIT 1",
            (tag, "%" + tag + "%"))
    if result is None or len(result) == 0:
        return None
    entry = MapEntry()
    entry.name = result[0][0]
    entry.author = result[0][1]
    entry.link = result[0][2]
    entry.website = result[0][3]
    entry.description = result[0][4]
    entry.short_description = result[0][5]
    entry.postId = result[0][6]
    entry.created_date = result[0][7]
    entry.updated_date = result[0][8]
    entry.up_votes = result[0][9]
    entry.down_votes = result[0][10]
    if len(result[0]) >= 12:
        entry.tags = result[0][11]
    return entry


def queryMapsByRandomTag(tag):
    if tag.lower() == "all":
        result = dbQuery("SELECT * FROM mmr_maps ORDER BY RAND() LIMIT 1", ())
    else:
        result = dbQuery(
            "SELECT name, author, link, website, description, short_description, postId, created_date, updated_date, up_votes, down_votes, mapTag FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE mapTag = %s GROUP BY(name) ORDER BY RAND() LIMIT 1",
            (tag,))
    if result is None or len(result) == 0:
        return None
    entry = MapEntry()
    entry.name = result[0][0]
    entry.author = result[0][1]
    entry.link = result[0][2]
    entry.website = result[0][3]
    entry.description = result[0][4]
    entry.short_description = result[0][5]
    entry.postId = result[0][6]
    entry.created_date = result[0][7]
    entry.updated_date = result[0][8]
    entry.up_votes = result[0][9]
    entry.down_votes = result[0][10]
    if len(result[0]) >= 12:
        entry.tags = result[0][11]
    return entry


def countMaps(tag):
    if tag == "all":
        results = dbQuery("SELECT COUNT(*) FROM mmr_maps ORDER BY name", ())
        if results is None or len(results) == 0:
            return 0
        return results[0][0]
    else:
        results = dbQuery(
            "SELECT COUNT(*) FROM mmr_maps m INNER JOIN mmr_maps_tags t ON m.name = t.mapName WHERE mapTag = %s OR name LIKE %s GROUP BY(name)",
            (tag, "%" + tag + "%"))
        return len(results)


def countTags():
    results = dbQuery("SELECT COUNT(DISTINCT(mapTag)) FROM mmr_maps_tags", ())
    if results is None or len(results) == 0:
        return 0
    return results[0][0]


class MapEntry:
    name = ""
    author = ""
    link = ""
    website = ""
    description = ""
    short_description = ""
    tags = ""
    postId = 0
    created_date = ""
    updated_date = ""
    up_votes = 0
    down_votes = 0

    def insertMap(self, tags):
        currentTime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        dbQuery(
            "INSERT INTO mmr_maps (name, author, link, website, description, short_description, postId, created_date, updated_date, up_votes, down_votes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (self.name, self.author, self.link, self.website, self.description, self.short_description, self.postId,
             currentTime, currentTime, 0, 0),
            True, False)
        for tag in tags.split(","):
            dbQuery(
                "INSERT INTO mmr_maps_tags (mapName, mapTag) VALUES (%s, %s)",
                (self.name, tag), True, False)

    def updateMapName(self, newName):
        dbQuery("UPDATE mmr_maps SET name = %s WHERE name = %s", (newName, self.name), True, False)
        dbQuery("UPDATE mmr_maps_tags SET mapName = %s WHERE mapName = %s", (newName, self.name), True, False)
        dbQuery("UPDATE mmr_maps_votes SET mapName = %s WHERE mapName = %s", (newName, self.name), True, False)
        self.name = newName

    def updateMapAuthor(self, newAuthor):
        dbQuery("UPDATE mmr_maps SET author = %s WHERE name = %s", (newAuthor, self.name), True, False)
        self.author = newAuthor

    def updateMapLink(self, newLink):
        dbQuery("UPDATE mmr_maps SET link = %s WHERE name = %s", (newLink, self.name), True, False)
        self.link = newLink

    def updateMapWebsite(self, newWebsite):
        dbQuery("UPDATE mmr_maps SET website = %s WHERE name = %s", (newWebsite, self.name), True, False)
        self.website = newWebsite

    def updateMapDescription(self, newDescription):
        dbQuery("UPDATE mmr_maps SET description = %s WHERE name = %s", (newDescription, self.name), True, False)
        self.description = newDescription

    def updateMapShortDescription(self, new_short_description):
        dbQuery("UPDATE mmr_maps SET short_description = %s WHERE name = %s", (new_short_description, self.name), True,
                False)
        self.short_description = new_short_description

    def updateMapTags(self, newTags):
        dbQuery("DELETE FROM mmr_maps_tags WHERE mapName = %s", (self.name,), True, False)
        for tag in newTags.split(","):
            dbQuery(
                "INSERT INTO mmr_maps_tags (mapName, mapTag) VALUES (%s, %s)",
                (self.name, tag), True, False)

    def updateMapVote(self, voter_id=None, up_vote=0, down_vote=0):
        vote = 0
        if up_vote == 1:
            vote = 1
        elif down_vote == 1:
            vote = -1
        if voter_id is None:
            return
        results = dbQuery("SELECT * FROM mmr_maps_votes WHERE mapName = %s AND user = %s", (self.name, voter_id,))
        if len(results) == 0:
            dbQuery(
                "INSERT INTO mmr_maps_votes (mapName, user, vote) VALUES (%s, %s, %s)",
                (self.name, voter_id, vote), True, False)
        else:
            current_vote = results[0][3]
            if current_vote == vote:
                up_vote = 0
                down_vote = 0
            elif current_vote == 1:
                up_vote = -1
            elif current_vote == -1:
                down_vote = -1
            dbQuery(
                "UPDATE mmr_maps_votes SET user = %s, vote = %s WHERE mapName = %s",
                (voter_id, vote, self.name,), True, False)
        dbQuery("UPDATE mmr_maps SET up_votes = %s, down_votes = %s WHERE name = %s",
                (self.up_votes + up_vote, self.down_votes + down_vote, self.name,), True, False)

    def updateMap(self, oldName):
        updated_date = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        dbQuery(
            "UPDATE mmr_maps SET name = %s, author = %s, link = %s, website = %s, description = %s, short_description = %s, updated_date = %s WHERE name = %s",
            (self.name, self.author, self.link, self.website, self.description, self.short_description,
             updated_date, oldName,), True, False)
        dbQuery("UPDATE mmr_maps_tags SET mapName = %s WHERE mapName = %s", (self.name, oldName), True, False)
        dbQuery("UPDATE mmr_maps_votes SET mapName = %s WHERE mapName = %s", (self.name, oldName), True, False)
        self.updateMapTags(self.tags)

    def deleteMap(self):
        dbQuery("DELETE FROM mmr_maps WHERE name = %s", (self.name,), True, False)
        dbQuery("DELETE FROM mmr_maps_tags WHERE mapName = %s", (self.name,), True, False)
        dbQuery("DELETE FROM mmr_maps_votes WHERE mapName = %s", (self.name,), True, False)
