import discord

from controller.mmr_calculations import mmr_calc
from model.config import config
from model.mmr_leaderboard import LeaderboardEntry


async def stats(user):
    player = LeaderboardEntry(user)
    if player.id == 0:
        embed = discord.embeds.Embed()
        embed.title = "Your Statistics"
        embed.color = 0x20872c
        embed.description = "Error: user is not registered for ranked matches. Use the `register` command to begin"
        return embed
    description = "MMR: {:.2f}\nGames this Decay: {:d}/{:d}\nGames this Season: {:d}/{:d} Game Limit\nVictories this Season: {:d}\nGames Total: {:d}\nVictories Total: {:d}\nSeason High MMR: {:.2f}".format(
        player.elo, player.gamesThisDecay, config["mmr-decay-games"], player.gamesThisSeason,
        config["placement-count"], player.gamesThisSeasonWon, player.gamesTotal, player.gamesTotalWon, player.seasonHigh)
    if config["mmr-decay-every"].lower() == "never":
        description = "MMR: {:.2f}\nGames this Season: {:d}/{:d} Game Limit\nVictories this Season: {:d}\nGames Total: {:d}\nVictories Total: {:d}\nSeason High MMR: {:.2f}".format(
            player.elo, player.gamesThisSeason, config["placement-count"], player.gamesThisSeasonWon,
            player.gamesTotal, player.gamesTotalWon, player.seasonHigh)
    embed = discord.embeds.Embed()
    embed.title = "Your Statistics"
    embed.color = 0x20872c
    embed.description = description
    return embed


async def register(user, tag):
    player = LeaderboardEntry(user)
    if player.id == 0:
        player.id = user
        player.elo = config["mmr-start-value"]
        player.discordTag = tag
        player.isBanned = False
        player.gamesThisDecay = 0
        player.gamesThisSeason = 0
        player.gamesThisSeasonWon = 0
        player.gamesTotal = 0
        player.gamesTotalWon = 0
        player.seasonHigh = player.elo
        player.insertUser()
        embed = discord.embeds.Embed()
        embed.title = "Registration"
        embed.color = 0x20872c
        embed.description = "<@{:d}> is now registered to play ranked games".format(user)
        return embed
    else:
        embed = discord.embeds.Embed()
        embed.title = "Registration"
        embed.color = 0x20872c
        embed.description = "<@{:d}> is already registered to play ranked games".format(user)
        return embed


async def score_match(args, user1, victory, updateStats, forceWin):
    if len(args) == 3 and forceWin:
        user1 = "<@" + str(args[1]) + ">"
        user2 = "<@" + str(args[2]) + ">"
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
            if player1.id == 0 or player2.id == 0:
                embed = discord.embeds.Embed()
                embed.title = "Manual Entry Results"
                embed.color = 0x20872c
                embed.description = "Error: Player not found on the leaderboard, please register using the `register` command to play ranked games"
                return embed
            player1OldElo = player1.elo
            player2OldElo = player2.elo
            mmr_calc(player1, player2, victory, updateStats)
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


async def placements(args, user):
    entry = LeaderboardEntry(user)
    placement_count = config["placement-count"]
    if entry.id == 0:
        embed = discord.embeds.Embed()
        embed.title = "Games Left"
        embed.color = 0x20872c
        embed.description = "Error: You must are not registered for ranked games. Type `!register` to get started with ranked"
        return embed
    else:
        embed = discord.embeds.Embed()
        embed.title = "Games Left"
        embed.color = 0x20872c
        if placement_count > entry.gamesThisSeason:
            embed.description = "You have to play {:d} more games to appear on the leaderboard".format(
                config["placement-count"] - entry.gamesThisSeason)
        else:
            embed.description = "You have reached your game limit for this season and now appear on the leaderboard"
        return embed


async def decay(args, user):
    entry = LeaderboardEntry(user)
    decayLimit = config["mmr-decay-games"]
    if entry.id == 0:
        embed = discord.embeds.Embed()
        embed.title = "Games Left"
        embed.color = 0x20872c
        embed.description = "Error: You must are not registered for ranked games. Type `!register` to get started with ranked"
        return embed
    else:
        embed = discord.embeds.Embed()
        embed.title = "Decay Games Left"
        embed.color = 0x20872c
        if decayLimit > entry.gamesThisSeason:
            embed.description = "You have to play {:d} more games to avoid decay".format(
                config["mmr-decay-games"] - entry.gamesThisDecay)
        else:
            embed.description = "You have to played {:d} out of {:d} games and will avoid decay".format(entry.gamesThisDecay, config["mmr-decay-games"])
        return embed
