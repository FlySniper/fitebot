import datetime

import discord

from model.config import config
from model.mmr_maps import MapEntry, queryMapsByTagOrName, queryMapsByRandomTagOrName, queryTags, queryMapsByName, \
    queryMapsByTag, queryMapsByRandomTag

EDIT_NAME = "edit name"
EDIT_AUTHOR = "edit author"
EDIT_LINK = "edit link"
EDIT_WEBSITE = "edit website"
EDIT_DESCRIPTION = "edit description"
EDIT_SHORT_DESCRIPTION = "edit short description"
EDIT_TAGS = "edit tags"
MAP_MODE_TAGS_OR_NAME = "tags or name"
MAP_MODE_TAGS = "tags"
MAP_MODE_NAME = "name"


class MapAddSession:
    def __init__(self, discordId):
        self.discordId = discordId
        self.expire = int((datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) + datetime.timedelta(
            minutes=30)).timestamp())
        self.mapEntry = MapEntry()
        self.state = "name"

    def addName(self, name):
        self.mapEntry.name = name
        self.state = "author"

    def addAuthor(self, author):
        self.mapEntry.author = author
        if config["enable-media-linking"]:
            self.state = "link"
        elif config["enable-website-linking"]:
            self.state = "website"
        else:
            self.state = "description"

    def addLink(self, link):
        if link.lower() == "skip":
            pass
        else:
            self.mapEntry.link = link
        if config["enable-website-linking"]:
            self.state = "website"
        else:
            self.state = "description"

    def addWebsite(self, website):
        if website.lower() == "skip":
            pass
        else:
            self.mapEntry.website = website
        self.state = "description"

    def addDescription(self, description):
        self.mapEntry.description = description
        self.state = "short_description"

    def addShortDescription(self, short_description):
        self.mapEntry.short_description = short_description
        self.state = "tags"

    def editName(self, name):
        self.mapEntry.updateMapName(name)

    def editAuthor(self, author):
        self.mapEntry.updateMapAuthor(author)

    def editLink(self, link):
        self.mapEntry.updateMapLink(link)

    def editWebsite(self, website):
        self.mapEntry.updateMapWebsite(website)

    def editDescription(self, description):
        self.mapEntry.updateMapDescription(description)

    def editShortDescription(self, short_description):
        self.mapEntry.updateMapShortDescription(short_description)

    def editTags(self, tags):
        self.mapEntry.updateMapTags(tags)

    def isExpired(self):
        currentTime = int((datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)).timestamp())
        return self.expire <= currentTime

    def getCurrentState(self):
        return self.state

    def setEditMode(self, mapQuery, editState):
        mapEntries = queryMapsByName(mapQuery, 0, 2)
        if len(mapEntries) != 1:
            return False
        self.mapEntry = mapEntries[0]
        self.state = editState
        return True

    def addMapToDatabase(self, tags):
        self.mapEntry.insertMap(tags)


mapAddSessions = {}


async def getMaps(tag, isRandom, pageNum, mapsPerPage, mode):
    startIndex = (pageNum - 1) * mapsPerPage
    if mode == MAP_MODE_TAGS_OR_NAME:
        mapEntries = queryMapsByTagOrName(tag, startIndex, mapsPerPage)
        errorMessage = "Error: Map name or tag not found"
        listTitle = "Maps Found ({tag})"
    elif mode == MAP_MODE_TAGS:
        mapEntries = queryMapsByTag(tag, startIndex, mapsPerPage)
        errorMessage = "Error: Map tag not found"
        listTitle = "Maps in Tag ({tag})"
    elif mode == MAP_MODE_NAME:
        mapEntries = queryMapsByName(tag, startIndex, mapsPerPage)
        errorMessage = "Error: Map name not found"
        listTitle = "Maps with Name ({tag})"
    else:
        mapEntries = []
        errorMessage = "Error: Map mode not found"
        listTitle = "Map Mode not Found"
    if isRandom:
        if mode == MAP_MODE_TAGS_OR_NAME:
            entry = queryMapsByRandomTagOrName(tag)
        elif mode == MAP_MODE_TAGS:
            entry = queryMapsByRandomTag(tag)
        else:
            entry = None
        if entry is None or entry.name == "":
            embed = discord.embeds.Embed()
            embed.title = "Map Error"
            embed.description = errorMessage
            return embed
        embed = discord.embeds.Embed()
        embed.title = "Your Random Map: {name}".format(name=entry.name)
        embed.description = "{description}\nAuthor: {author}".format(description=entry.description, author=entry.author)
        embed.set_image(url=entry.link)
        embed.color = 0x20872c
        return embed
    if len(mapEntries) == 0:
        embed = discord.embeds.Embed()
        embed.title = "Map Error"
        embed.description = errorMessage
        return embed

    if len(mapEntries) == 1:
        entry = mapEntries[0]
        embed = discord.embeds.Embed()
        embed.title = "Map Found: {name}".format(name=entry.name)
        embed.description = "{description}\nAuthor: {author}".format(description=entry.description, author=entry.author)
        if config["enable-media-linking"] and entry.link is not None and len(entry.link) > 0:
            embed.set_image(url=entry.link)
        embed.color = 0x20872c
        if config["enable-website-linking"] and entry.website is not None and len(entry.website) > 0:
            embed.url = entry.website
            return embed
        else:
            return embed

    description = "***Map name (version) — Summary***"
    fieldValue = ""
    count = startIndex + 1
    for entry in mapEntries:
        fieldValue += "`{count}` {name} - {short_description}\n".format(count=count, name=entry.name,
                                                                        short_description=entry.short_description)
        count += 1

    embed = discord.embeds.Embed()
    embed.title = listTitle.format(tag=tag)
    embed.description = description
    embed.add_field(name="{:d}-{:d}".format(startIndex + 1, startIndex + mapsPerPage),
                    value=fieldValue)
    embed.color = 0x20872c
    return embed


async def getMapTags(start, end):
    startIndex = start * end
    description = "***Map tags***"
    fieldValue = getTagsField(start, end)

    embed = discord.embeds.Embed()
    embed.title = "Tags Found"
    embed.description = description
    embed.add_field(name="{:d}-{:d}".format(startIndex + 1, startIndex + end),
                    value=fieldValue)
    embed.color = 0x20872c
    return embed


def getMapsField(tag, startIndex, mapsPerPage):
    mapEntries = queryMapsByTagOrName(tag, startIndex, mapsPerPage)
    fieldValue = ""
    count = startIndex + 1
    for entry in mapEntries:
        fieldValue += "`{count}` {name} - {short_description}\n".format(count=count, name=entry.name,
                                                                        short_description=entry.short_description)
        count += 1
    return fieldValue


def getMapTagField(tag, startIndex, mapsPerPage):
    mapEntries = queryMapsByTag(tag, startIndex, mapsPerPage)
    fieldValue = ""
    count = startIndex + 1
    for entry in mapEntries:
        fieldValue += "`{count}` {name} - {short_description}\n".format(count=count, name=entry.name,
                                                                        short_description=entry.short_description)
        count += 1
    return fieldValue


def getMapNameField(tag, startIndex, mapsPerPage):
    mapEntries = queryMapsByName(tag, startIndex, mapsPerPage)
    fieldValue = ""
    count = startIndex + 1
    for entry in mapEntries:
        fieldValue += "`{count}` {name} - {short_description}\n".format(count=count, name=entry.name,
                                                                        short_description=entry.short_description)
        count += 1
    return fieldValue


def getTagsField(startIndex, mapsPerPage):
    tags = queryTags(startIndex, mapsPerPage)
    fieldValue = ""
    count = startIndex + 1
    for tag in tags:
        fieldValue += "`{count}` {tag}\n".format(count=count, tag=tag)
        count += 1
    return fieldValue


async def delMap(name):
    mapEntries = queryMapsByName(name, 0, 25)
    if len(mapEntries) != 1:
        embed = discord.embeds.Embed()
        embed.title = "Delete Map Error"
        embed.description = "Error: Exact Map name not found"
        return embed
    entry = mapEntries[0]
    embed = discord.embeds.Embed()
    embed.title = "Map Deleted: {name}".format(name=entry.name)
    embed.description = "{description}\nAuthor: {author}".format(description=entry.description, author=entry.author)
    embed.set_image(url=entry.link)
    embed.color = 0x20872c
    entry.deleteMap()
    return embed


async def startMapAddSession(author):
    discordId = author.id
    if discordId in mapAddSessions.keys():
        mapAddSession = mapAddSessions[discordId]
        if not mapAddSession.isExpired():
            embed = discord.embeds.Embed()
            embed.title = "Map Add Error"
            embed.description = "Error: User is already adding/editing a map, please finish adding the map"
            return embed
    mapAddSessions[discordId] = MapAddSession(discordId)
    embed = discord.embeds.Embed()
    embed.title = "Map Add"
    embed.description = "Map Add session started, please check your DMs"
    embed.color = 0x20872c
    dmChannel = await author.create_dm()
    await dmChannel.send("Please enter the map name:")
    return embed


async def startMapEditSession(author, mapName, editType):
    discordId = author.id
    if discordId in mapAddSessions.keys():
        mapAddSession = mapAddSessions[discordId]
        if not mapAddSession.isExpired():
            embed = discord.embeds.Embed()
            embed.title = "Map Edit Error"
            embed.description = "Error: User is already adding/editing a map, please finish adding the map"
            return embed
    session = MapAddSession(discordId)
    if not session.setEditMode(mapName, editType):
        embed = discord.embeds.Embed()
        embed.title = "Map Edit Error"
        embed.description = "Error: Map query does not resolve to exactly one map"
        return embed
    mapAddSessions[discordId] = session
    embed = discord.embeds.Embed()
    embed.title = "Map Edit"
    embed.description = "Map Edit session started, please check your DMs"
    embed.color = 0x20872c
    dmChannel = await author.create_dm()
    if editType == EDIT_NAME:
        await dmChannel.send("Please enter the new map name:")
    elif editType == EDIT_AUTHOR:
        await dmChannel.send("Please enter the new map author:")
    elif editType == EDIT_LINK:
        await dmChannel.send("Please enter the new map media link:")
    elif editType == EDIT_WEBSITE:
        await dmChannel.send("Please enter the new map website:")
    elif editType == EDIT_DESCRIPTION:
        await dmChannel.send("Please enter the new map description:")
    elif editType == EDIT_SHORT_DESCRIPTION:
        await dmChannel.send("Please enter the new map short description:")
    elif editType == EDIT_TAGS:
        await dmChannel.send("Please enter the new tags for the map, separated by a comma without spaces:")
    return embed


def isInMapAddSession(discordId):
    return discordId in mapAddSessions.keys()


def getMapAddSession(discordId):
    return mapAddSessions[discordId]


def removeMapAddSession(discordId):
    try:
        del mapAddSessions[discordId]
    except KeyError:
        pass
