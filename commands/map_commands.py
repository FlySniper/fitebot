import datetime
import random

import discord

from model.config import config
from model.mmr_maps import MapEntry, queryMapsByTag, queryMapsByRandomTag


async def getMaps(tag, isRandom, pageNum, mapsPerPage):
    startIndex = (pageNum - 1) * mapsPerPage
    mapEntries = queryMapsByTag(tag, startIndex, mapsPerPage)
    if isRandom:
        entry = queryMapsByRandomTag(tag)
        if entry is None or entry.name == "":
            embed = discord.embeds.Embed()
            embed.title = "Map Error"
            embed.description = "Error: Map tag not found"
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
        embed.description = "Error: Map tag not found"
        return embed

    if len(mapEntries) == 1:
        entry = mapEntries[0]
        embed = discord.embeds.Embed()
        embed.title = "Map Found: {name}".format(name=entry.name)
        embed.description = "{description}\nAuthor: {author}".format(description=entry.description, author=entry.author)
        embed.set_image(url=entry.link)
        embed.color = 0x20872c
        return embed

    description = "***Map name (version) — Author***"
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


def getMapsField(tag, startIndex, mapsPerPage):
    mapEntries = queryMapsByTag(tag, startIndex, mapsPerPage)
    fieldValue = ""
    count = startIndex + 1
    for entry in mapEntries:
        fieldValue += "`{count}` {name} - {author}\n".format(count=count, name=entry.name, author=entry.author)
        count += 1
    return fieldValue
