import discord

from model.config import config
from model.mmr_maps import countMaps


async def reactWithPaginationEmojis(message):
    await message.add_reaction("\u23EA")
    await message.add_reaction("\u2B05")
    await message.add_reaction("\u27A1")
    await message.add_reaction("\u23E9")


async def arrowEmojiReactionMapTag(embed, emoji, reaction, getFields):
    fieldCount = len(embed.fields)
    if fieldCount > 0:
        field = embed.fields[0]
        splt = field.name.split("-")
        tag = embed.title[12:-1]
        numEntries = countMaps(tag)
        start = int(splt[0]) - 1
        count = int(splt[1]) - start
        if emoji == "⬅":
            start -= count
        elif emoji == "➡":
            start += count
        elif emoji == "⏩":
            start = numEntries - count
        elif emoji == "⏪":
            start = 0
        else:
            return
        start = max(0, min(start, numEntries))
        fieldValue = getFields(tag, start, count)
        if fieldValue is None or fieldValue == "":
            return
        embed.set_field_at(0, name="{:d}-{:d}".format(start + 1, start + count),
                           value=fieldValue)
        await reaction.message.edit(embed=embed)


async def arrowEmojiReaction(embed, emoji, reaction, numEntries, getFields):
    fieldCount = len(embed.fields)
    if fieldCount > 0:
        field = embed.fields[0]
        splt = field.name.split("-")
        start = int(splt[0]) - 1
        count = int(splt[1]) - start
        if emoji == "⬅":
            start -= count
        elif emoji == "➡":
            start += count
        elif emoji == "⏩":
            start = numEntries - count
        elif emoji == "⏪":
            start = 0
        else:
            return
        start = max(0, min(start, numEntries))
        fieldValue = getFields(start, count)
        if fieldValue is None or fieldValue == "":
            return
        embed.set_field_at(0, name="{:d}-{:d}".format(start + 1, start + count),
                           value=fieldValue)
        await reaction.message.edit(embed=embed)

