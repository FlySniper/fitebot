import datetime
import random

import discord

from commands.map_commands import getMaps
from model.config import config
from model.mmr_leaderboard import LeaderboardEntry
from model.mmr_queue import QueueEntry, queryQueue


async def queue(id, queueName, timeLimit, channel, bot):
    leaderboardEntry = LeaderboardEntry(id)
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
    queueConfig = matchmakingConfig[queueName]
    matchmakingEnabled = queueConfig["uses-matchmaking"]
    if (leaderboardEntry is None or leaderboardEntry.id == 0) and matchmakingEnabled:
        embed = discord.embeds.Embed()
        embed.title = "Queue Error"
        embed.color = 0x20872c
        embed.description = "Error: You are not registered to play ranked matches, please use the `register` command in the discord"
        await channel.send(embed=embed)
        return
    if matchmakingEnabled:
        elo = leaderboardEntry.elo
    else:
        elo = 1.0

    futureTime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    futureTime += datetime.timedelta(minutes=timeLimit)

    currentQueue = queryQueue(queueName)
    if len(currentQueue) == 0:
        matchmakingChannel = queueConfig["channel"]
        channelObj = bot.get_channel(matchmakingChannel)
        queueEntry = QueueEntry(None, None)
        queueEntry.id = id
        if matchmakingEnabled:
            queueEntry.elo = elo
        else:
            queueEntry.elo = 1
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
            embed.description = queueConfig["notification-text"].replace("queueTime", str(int(futureTime.timestamp())))
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

                currentDateTime = datetime.datetime.now(datetime.timezone.utc)
                currentDateTime = currentDateTime.replace(tzinfo=None)
                if currentDateTime >= entry.exitDate:
                    entry.deleteUser()
                    continue

                if entry.id == id:
                    embed = discord.embeds.Embed()
                    embed.title = "Queue Error"
                    embed.description = "You are already in the `" + queueName + "` queue"
                    await channel.send(embed=embed)
                    return

                if matchmakingBand > entry.elo - averageElo > -matchmakingBand:
                    validPlayers.append(entry.id)
                    validQueueEntries.append(entry)
                    averageElo += entry.elo / len(validPlayers)
                if len(validPlayers) >= requiredPlayers:
                    break
            if len(validPlayers) < requiredPlayers:
                queueEntry = QueueEntry(None, None)
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
                if queueConfig["post-notification"] and len(validPlayers) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Queue"
                    embed.color = 0x20872c
                    embed.description = queueConfig["notification-text"].replace("queueTime", str(int(futureTime.timestamp())))
                    await channelObj.send(embed=embed)
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
            mapEmbed = await getMaps(queueConfig["maptags"], True, 1, 1)
            embed = discord.embeds.Embed()
            embed.title = "Queue"
            embed.color = 0x20872c
            embed.description = "Game found! Head to <#" + str(matchmakingChannel) + ">"
            await channel.send(embed=embed)
            await channelObj.send(finalText)
            for entry in validQueueEntries:
                entry.deleteUser()
            await channelObj.send(embed=mapEmbed)
        else:
            for entry in currentQueue:
                currentDateTime = datetime.datetime.now(datetime.timezone.utc)
                currentDateTime = currentDateTime.replace(tzinfo=None)
                if entry.id == id and currentDateTime >= entry.exitDate:
                    entry.deleteUser()
                    newEntry = QueueEntry(None, None)
                    newEntry.id = id
                    if matchmakingEnabled:
                        newEntry.elo = elo
                    else:
                        newEntry.elo = 1
                    newEntry.queueName = queueName
                    newEntry.exitDate = futureTime
                    newEntry.insertUser()
                    embed = discord.embeds.Embed()
                    embed.title = "Queue"
                    embed.color = 0x20872c
                    embed.description = "You have entered the `" + queueName + "` queue"
                    await channel.send(embed=embed)
                    if queueConfig["post-notification"]:
                        embed = discord.embeds.Embed()
                        embed.title = "Queue"
                        embed.color = 0x20872c
                        embed.description = queueConfig["notification-text"].replace("queueTime", str(int(futureTime.timestamp())))
                        await channelObj.send(embed=embed)
                    return
                elif entry.id == id:
                    embed = discord.embeds.Embed()
                    embed.title = "Queue Error"
                    embed.description = "You are already in the `" + queueName + "` queue"
                    await channel.send(embed=embed)
                    return


async def cancel(id, queueName, bot):
    entry = QueueEntry(userId=id, queueName=queueName)
    currentDateTime = datetime.datetime.now(datetime.timezone.utc)
    currentDateTime = currentDateTime.replace(tzinfo=None)
    if entry.id == 0:
        embed = discord.embeds.Embed()
        embed.title = "Cancel Error"
        embed.description = "Error: user is not queued for a match in this queue"
        return embed
    if entry.exitDate <= currentDateTime:
        entry.deleteUser()
        embed = discord.embeds.Embed()
        embed.color = 0xFF0000
        embed.title = "Cancel"
        embed.description = "Time in queue expired"
        return embed
    entry.deleteUser()
    embed = discord.embeds.Embed()
    embed.title = "Cancel"
    embed.color = 0xFF0000
    embed.description = "You have left the " + queueName + " queue"
    matchmakingEmbed = discord.embeds.Embed()
    matchmakingEmbed.title = "Cancel"
    matchmakingEmbed.color = 0xFF0000
    matchmakingEmbed.description = "Someone has left the `" + queueName + "` queue"
    matchmakingConfig = config["matchmaking"]
    queueConfig = matchmakingConfig[queueName]
    matchmakingChannel = queueConfig["channel"]
    channelObj = bot.get_channel(matchmakingChannel)
    await channelObj.send(embed=matchmakingEmbed)
    return embed
