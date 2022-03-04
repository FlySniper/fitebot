import discord

from controller.mmr_calculations import mmr_calc
from model.mmr_leaderboard import LeaderboardEntry


async def register(client, user, tag):
    player = LeaderboardEntry()
    player.id = user
    player.elo = client.config["mmr-start-value"]
    player.discordTag = tag
    player.isBanned = False
    player.gamesThisDecay = 0
    player.gamesThisSeason = 0
    player.gamesThisSeasonWon = 0
    player.seasonHigh = player.elo
    player.insertUser()
    embed = discord.embeds.Embed()
    embed.title = "Registration"
    embed.color = 0x20872c
    embed.description = "<@{:d}> is now registered to play ranked games".format(user)
    return embed


async def score_match(args, client, user1, victory, updateStats, forceWin):
    if len(args) == 3 and forceWin:
        user1 = args[1]
        user2 = args[2]
    elif len(args) == 2 and not forceWin:
        user2 = args[1]
    else:
        embed = discord.embeds.Embed()
        embed.title = "Manual Entry Results"
        embed.color = 0x20872c
        embed.description = "Error: You must @ one opponent as your argument `!iwin|!ilost @opponent#1234`"
        return embed
    if (user1.startswith("<@") or user1.startswith("<!@")) and user1.endswith(">") and (
            user2.startswith("<@") or user2.startswith("<!@")) and user2.endswith(">"):
        id1 = user1.replace("<", "").replace("@", "").replace("!", "").replace(">", "")
        id2 = user2.replace("<", "").replace("@", "").replace("!", "").replace(">", "")
        if id1.isnumeric() and id2.isnumeric() and id1 != id2:
            player1 = LeaderboardEntry(int(id1))
            player2 = LeaderboardEntry(int(id2))
            if player1 is None or player2 is None:
                embed = discord.embeds.Embed()
                embed.title = "Manual Entry Results"
                embed.color = 0x20872c
                embed.description = "Error: Player not found on the leaderboard, please register to play ranked games"
                return embed
            player1OldElo = player1.elo
            player2OldElo = player2.elo
            mmr_calc(client.config, player1, player2, victory, updateStats)
            description = "<@{:d}> won and went from {:.2f} to {:.2f} MMR\n\n<@{:d}> lost and went from {:.2f} to {:.2f} MMR"
            if victory == 1:
                description = description.format(player1.id, player1OldElo, player1.elo, player2.id, player2OldElo,
                                                 player2.elo)
            elif victory == 2:
                description = description.format(player2.id, player2OldElo, player2.elo, player1.id, player1OldElo,
                                                 player1.elo)
            else:
                description = "<@{:d}> went from {:.2f} to {:.2f} MMR\n\n<@{:d}> went from {:.2f} to {:.2f} MMR".format(
                    player1.id, player1OldElo, player1.elo, player2.id, player2OldElo, player2.elo)
            embed = discord.embeds.Embed()
            embed.title = "Manual Entry Results"
            embed.color = 0x20872c
            embed.description = description
            return embed
        else:
            embed = discord.embeds.Embed()
            embed.title = "Manual Entry Results"
            embed.color = 0x20872c
            embed.description = "Error: You must @ one opponent as your argument `!iwin|!ilost @opponent#1234`"
            return embed
    else:
        embed = discord.embeds.Embed()
        embed.title = "Manual Entry Results"
        embed.color = 0x20872c
        embed.description = "Error: You must @ one opponent as your argument `!iwin|!ilost @opponent#1234`"
        return embed
