import datetime
import random

import discord

from model.config import config
from model.mmr_leaderboard import LeaderboardEntry
from model.mmr_queue import QueueEntry, queryQueue


async def queue(id, queueName, timeLimit, channel, bot):
    leaderboardEntry = LeaderboardEntry(id)
    if leaderboardEntry is None:
        embed = discord.embeds.Embed()
        embed.title = "Queue Error"
        embed.color = 0x20872c
        embed.description = "Error: You are not registered to play ranked matches, please use `!register` in the discord"
        await channel.send(embed=embed)
        return
    elo = leaderboardEntry.elo

    matchmakingConfig = config["matchmaking"]
    if queueName not in matchmakingConfig.keys():
        embed = discord.embeds.Embed()
        embed.title = "Queue Error"
        description = "Error: queue not found, example queue commands are:"
        for key in matchmakingConfig.keys():
            description += "\n\t!queue " + key
        embed.description = description
        await channel.send(embed=embed)
        return

    futureTime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    futureTime += datetime.timedelta(minutes=timeLimit)

    currentQueue = queryQueue(queueName)
    if len(currentQueue) == 0:
        queueConfig = matchmakingConfig[queueName]
        matchmakingChannel = queueConfig["channel"]
        channelObj = bot.get_channel(matchmakingChannel)
        queueEntry = QueueEntry(None)
        queueEntry.id = id
        queueEntry.elo = elo
        queueEntry.queueName = queueName
        queueEntry.exitDate = futureTime
        queueEntry.insertUser()
        embed = discord.embeds.Embed()
        embed.title = "Queue"
        embed.color = 0x20872c
        embed.description = "You have entered the `" + queueName + "` queue"
        await channel.send(embed=embed)
        if queueConfig["post-notification"]:
            embed = discord.embeds.Embed()
            embed.title = "Queue"
            embed.color = 0x20872c
            embed.description = queueConfig["notification-text"]
            await channelObj.send(embed=embed)
        return
    else:
        queueConfig = matchmakingConfig[queueName]
        matchmakingChannel = queueConfig["channel"]
        channelObj = bot.get_channel(matchmakingChannel)
        requiredPlayers = queueConfig["players"]
        requiredTeams = queueConfig["teams"]
        if len(currentQueue) + 1 >= requiredPlayers:
            validPlayers = [id]
            validQueueEntries = []
            averageElo = elo
            matchmakingBand = queueConfig["matchmaking-band"]
            for entry in currentQueue:
                if matchmakingBand > entry.elo - averageElo > -matchmakingBand:
                    validPlayers.append(entry.id)
                    validQueueEntries.append(entry)
                    averageElo += entry.elo / len(validPlayers)
                if len(validPlayers) >= requiredPlayers:
                    break
            if len(validPlayers) < requiredPlayers:
                queueEntry = QueueEntry(None)
                queueEntry.id = id
                queueEntry.elo = elo
                queueEntry.queueName = queueName
                queueEntry.exitDate = futureTime
                queueEntry.insertUser()
                embed = discord.embeds.Embed()
                embed.title = "Queue"
                embed.color = 0x20872c
                embed.description = "You have entered the `" + queueName + "` queue"
                await channel.send(embed=embed)
                return
            teams = [[] for team in range(0, requiredTeams)]
            random.shuffle(validPlayers)
            for i in range(0, len(validPlayers)):
                teams[i % requiredTeams].append(validPlayers[i])
            finalText = "Fite!"
            for i in range(0, len(teams)):
                finalText += "\nTeam " + str(i + 1) + ":"
                for j in range(0, len(teams[i])):
                    finalText += " <@" + str(teams[i][j]) + ">"
            if queueConfig["uses-bans"]:
                finalText += "\nBans Underway"
                # TODO Implement Bans
            # TODO Implement Random Maps
            embed = discord.embeds.Embed()
            embed.title = "Queue"
            embed.color = 0x20872c
            embed.description = "Game found! Head to <#" + str(matchmakingChannel) + ">"
            await channel.send(embed=embed)
            await channelObj.send(finalText)
            for entry in validQueueEntries:
                entry.deleteUser()
