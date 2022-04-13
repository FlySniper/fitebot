import discord

from model.config import config
from model.mmr_leaderboard import LeaderboardEntry


async def setElo(adminId, user, elo):
    player = LeaderboardEntry(user)
    if player.id == 0:
        embed = discord.embeds.Embed()
        embed.title = "Set Elo Error"
        embed.description = "Error: provided user is not registered for ranked matches"
        return embed
    oldElo = player.elo
    player.elo = elo
    player.updateUser()
    embed = discord.embeds.Embed()
    embed.title = "Set Elo"
    embed.color = 0x20872c
    embed.description = "<@" + str(adminId) + ">" + " set player ID: " + str(player.id) + " from " + str(oldElo) + " to " + str(elo)
    return embed
