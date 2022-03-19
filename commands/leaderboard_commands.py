import discord

from model.config import config
from model.mmr_leaderboard import LeaderboardEntry, queryLeaderboard


async def displayLeaderboard(start, count):
    leaderboardText = config["leaderboard-text"]
    entries = queryLeaderboard(start, count, 0)
    embed = discord.embeds.Embed()
    embed.title = "Leaderboard"
    embed.description = leaderboardText
    index = 0
    fieldValue = ""
    for entry in entries:
        emoji = getEmoji(entry.elo)
        fieldValue += "`{:d}`{:s}{:.128s} - - - ({:.2f})\n".format(start + 1 + index, emoji, entry.discordTag,
                                                                   entry.elo)
        index += 1

    embed.add_field(name="{:d}-{:d}".format(start + 1, count),
                    value=fieldValue)
    return embed


def getEmoji(elo):
    scales = config["mmr-scales"]
    emoji = ""
    for scale in scales:
        for scaleName in scale:
            scaleObj = scale[scaleName]
            if elo >= scaleObj["start"]:
                emoji = scaleObj["emoji"]

    return emoji
