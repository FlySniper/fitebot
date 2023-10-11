import discord

from model.config import config
from model.mmr_leaderboard import queryLeaderboard, countLeaderboard, querySeasonHighLeaderboard


async def displayLeaderboard(start, count, season=0):
    leaderboardText = config["leaderboard-text"]
    embed = discord.embeds.Embed()
    if season == 0:
        embed.title = "Leaderboard"
    else:
        embed.title = f"Leaderboard from Season {season}"
    embed.description = leaderboardText
    numEntries = countLeaderboard(0)
    start = max(0, min(start, numEntries - 1))
    fieldValue = generateLeaderboardField(start, count, season=season)

    embed.add_field(name="{:d}-{:d}".format(start + 1, start + count),
                    value=fieldValue)
    return embed


def generateLeaderboardField(start, count, season=0):
    entries = queryLeaderboard(start, count, config["placement-count"], season=season)
    index = 0
    fieldValue = ""
    for entry in entries:
        emoji = getEmoji(entry.elo)
        fieldValue += "`{:d}`{:s}<@!{:d}> - - - ({:.2f})\n".format(start + 1 + index, emoji, entry.id,
                                                                   entry.elo)
        index += 1
    return fieldValue


async def displaySeasonHighs(start, count):
    leaderboardText = config["season-high-leaderboard-text"]
    embed = discord.embeds.Embed()
    embed.title = "Season High Leaderboard"
    embed.description = leaderboardText
    numEntries = countLeaderboard(0)
    start = max(0, min(start, numEntries - 1))
    fieldValue = generateSeasonHighsField(start, count)

    embed.add_field(name="{:d}-{:d}".format(start + 1, start + count),
                    value=fieldValue)
    return embed


def generateSeasonHighsField(start, count):
    entries = querySeasonHighLeaderboard(start, count, config["placement-count"])
    index = 0
    fieldValue = ""
    for entry in entries:
        emoji = getEmoji(entry.elo)
        fieldValue += "`{:d}`{:s}<@!{:d}> - - - ({:.2f})\n".format(start + 1 + index, emoji, entry.id,
                                                                   entry.seasonHigh)
        index += 1
    return fieldValue


def getEmoji(elo):
    scales = config["mmr-scales"]
    emoji = ""
    for scale in scales:
        for scaleName in scale:
            scaleObj = scale[scaleName]
            if elo >= scaleObj["start"]:
                emoji = scaleObj["emoji"]

    return emoji
