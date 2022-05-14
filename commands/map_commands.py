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

    description = "***Map name (version) — Code***"
    for entry in mapEntries:
        description += "\n{name} - {author}".format(name=entry.name, author=entry.author)

    embed = discord.embeds.Embed()
    embed.title = "Maps Found"
    embed.description = description
    embed.color = 0x20872c
    return embed
