import datetime
import random

import discord

from model.config import config
from model.mmr_maps import MapEntry, queryMapsByTag, queryMapsByRandomTag, queryTags

EDIT_NAME = "edit name"
EDIT_AUTHOR = "edit author"
EDIT_LINK = "edit link"
EDIT_DESCRIPTION = "edit description"
EDIT_TAGS = "edit tags"


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
        self.state = "link"

    def addLink(self, link):
        self.mapEntry.link = link
        self.state = "description"

    def addDescription(self, description):
        self.mapEntry.description = description
        self.state = "tags"

    def editName(self, name):
        self.mapEntry.updateMapName(name)

    def editAuthor(self, author):
        self.mapEntry.updateMapAuthor(author)

    def editLink(self, link):
        self.mapEntry.updateMapLink(link)

    def editDescription(self, description):
        self.mapEntry.updateMapDescription(description)

    def editTags(self, tags):
        self.mapEntry.updateMapTags(tags)

    def isExpired(self):
        currentTime = int((datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)).timestamp())
        return self.expire <= currentTime

    def getCurrentState(self):
        return self.state

    def setEditMode(self, mapQuery, editState):
        mapEntries = queryMapsByTag(mapQuery, 0, 2)
        if len(mapEntries) != 1:
            return False
        self.mapEntry = mapEntries[0]
        self.state = editState
        return True

    def addMapToDatabase(self, tags):
        self.mapEntry.insertMap(tags)


mapAddSessions = {}


async def getMaps(tag, isRandom, pageNum, mapsPerPage):
    startIndex = (pageNum - 1) * mapsPerPage
    mapEntries = queryMapsByTag(tag, startIndex, mapsPerPage)
    if isRandom:
        entry = queryMapsByRandomTag(tag)
        if entry is None or entry.name == "":
            embed = discord.embeds.Embed()
            embed.title = "Map Error"
            embed.description = "Error: Map name or tag not found"
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
        embed.description = "Error: Map name or tag not found"
        return embed

    if len(mapEntries) == 1:
        entry = mapEntries[0]
        embed = discord.embeds.Embed()
        embed.title = "Map Found: {name}".format(name=entry.name)
        embed.description = "{description}\nAuthor: {author}".format(description=entry.description, author=entry.author)
        embed.set_image(url=entry.link)
        embed.color = 0x20872c
        return embed

    description = "***Map name (version) ??? Author***"
    fieldValue = ""
    count = startIndex + 1
    for entry in mapEntries:
        fieldValue += "`{count}` {name} - {author}\n".format(count=count, name=entry.name, author=entry.author)
        count += 1

    embed = discord.embeds.Embed()
    embed.title = "Maps Found ({tag})".format(tag=tag)
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
    mapEntries = queryMapsByTag(tag, startIndex, mapsPerPage)
    fieldValue = ""
    count = startIndex + 1
    for entry in mapEntries:
        fieldValue += "`{count}` {name} - {author}\n".format(count=count, name=entry.name, author=entry.author)
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
    mapEntries = queryMapsByTag(name, 0, 25)
    if len(mapEntries) != 1:
        embed = discord.embeds.Embed()
        embed.title = "Delete Map Error"
        embed.description = "Error: Map name or tag not found"
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
        await dmChannel.send("Please enter the new map link:")
    elif editType == EDIT_DESCRIPTION:
        await dmChannel.send("Please enter the new map description:")
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
