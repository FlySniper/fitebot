import discord
from threading import Thread

import mysql

from commands.admin_commands import setElo
from commands.leaderboard_commands import displayLeaderboard, generateLeaderboardField, generateSeasonHighsField
from commands.mmr_commands import score_match, register, stats, gameLimit, decay
from commands.queue_commands import queue, cancel
from controller.pagination import reactWithPaginationEmojis
from model import db
from model.config import refreshConfig, config
from model.mmr_leaderboard import countLeaderboard

prefix = config["command-prefix"]


class MyClient(discord.Client):

    async def on_ready(self):
        print("Bot Starting")
        db.connection = mysql.connector.connect(
            host=config["mysql-hostname"],
            database=config["mysql-database"],
            user=config["mysql-user"],
            password=config["mysql-password"],
            autocommit=True
        )
        db.connection.time_zone = '+00:00'
        refreshThread = Thread(target=refreshConfig)
        refreshThread.start()

    async def on_message(self, message):
        if not message.content.startswith(prefix):
            return
        commandArgs = message.content[1:].lower().split(" ")
        print(commandArgs[0])
        if isinstance(message.channel, discord.channel.DMChannel):
            print("DM Command: " + message.content)
            if commandArgs[0] == "queue":
                queueTime = 30
                embed = discord.embeds.Embed()
                embed.title = "Queue Error"
                embed.description = "Error: Please enter a number for the time in minutes you would like to queue for"
                if len(commandArgs) == 3:
                    try:
                        queueTime = int(commandArgs[2])
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Queue Error"
                    description = "Error: Please enter a valid queue name:"
                    for key in config["matchmaking"].keys():
                        description += "\n\t!queue " + key
                    embed.description = description
                    await message.channel.send(
                        embed=embed)
                    return
                await queue(message.author.id, commandArgs[1], queueTime, message.channel, self)
            if commandArgs[0] == "iban":
                pass
            if commandArgs[0] == "stopbans":
                pass
            if commandArgs[0] == "accept":
                pass
            if commandArgs[0] == "cancel":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Cancel Error"
                    description = "Error: Please enter a valid queue name:"
                    for key in config["matchmaking"].keys():
                        description += "\n\t!queue " + key
                    embed.description = description
                    await message.channel.send(
                        embed=embed)
                    return
                await message.channel.send(embed=await cancel(message.author.id, commandArgs[1], self))
        if message.channel.id in config["command-channels"] or "all" in config["command-channels"]:
            if commandArgs[0] == "maps":
                pass
            if commandArgs[0] == "season":
                pass
            if commandArgs[0] == "stats":
                await message.channel.send(embed=await stats(message.author.id))
            if commandArgs[0] == "decay":
                await message.channel.send(embed=await decay(commandArgs, message.author.id))
            if commandArgs[0] == "gamelimit":
                await message.channel.send(embed=await gameLimit(commandArgs, message.author.id))
            if commandArgs[0] == "register":
                await message.channel.send(embed=await register(message.author.id,
                                                                message.author.name + "#" + str(
                                                                    message.author.discriminator)))
            if commandArgs[0] == "iwin" or commandArgs[0] == "iwon":
                await message.channel.send(
                    embed=await score_match(commandArgs, "<@" + str(message.author.id) + ">", 1, True, False))
            if commandArgs[0] == "ilose" or commandArgs[0] == "ilost" or commandArgs[0] == "iloss":
                await message.channel.send(
                    embed=await score_match(commandArgs, "<@" + str(message.author.id) + ">", 2, True, False))
            if commandArgs[0] == "help" or commandArgs[0] == "ranked":
                pass
            if commandArgs[0] == "leaderboard":
                start = 1
                count = 25
                embed = discord.embeds.Embed()
                embed.title = "Leaderboard Error"
                embed.description = "Error: Please enter one or two valid numbers for the leaderboard range"
                if len(commandArgs) == 2:
                    try:
                        start = int(commandArgs[1])
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                elif len(commandArgs) == 3:
                    try:
                        start = int(commandArgs[1])
                        count = min(int(commandArgs[2]), 25)
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                elif len(commandArgs) != 1:
                    await message.channel.send(
                        embed=embed)
                    return
                leaderboardMessage = await message.channel.send(
                    embed=await displayLeaderboard(start - 1, count))
                await reactWithPaginationEmojis(leaderboardMessage)
            if commandArgs[0] == "seasonhighs":
                start = 1
                count = 25
                embed = discord.embeds.Embed()
                embed.title = "Leaderboard Error"
                embed.description = "Error: Please enter one or two valid numbers for the leaderboard range"
                if len(commandArgs) == 2:
                    try:
                        start = int(commandArgs[1])
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                elif len(commandArgs) == 3:
                    try:
                        start = int(commandArgs[1])
                        count = min(int(commandArgs[2]), 25)
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                elif len(commandArgs) != 1:
                    await message.channel.send(
                        embed=embed)
                    return
                leaderboardMessage = await message.channel.send(
                    embed=await displayLeaderboard(start - 1, count))
                await reactWithPaginationEmojis(leaderboardMessage)
            if commandArgs[0] == "logs":
                pass
            if commandArgs[0] == "startbans":
                pass
        if message.channel.id in config["admin-channels"]:
            if commandArgs[0] == "ban":
                pass
            if commandArgs[0] == "unban":
                pass
            if commandArgs[0] == "setelo":
                if len(commandArgs) == 3:
                    embed = discord.embeds.Embed()
                    embed.title = "Set Elo"
                    embed.description = "Error: Please enter a valid discord ID (not an @) and an elo amount"
                    try:
                        userId = int(commandArgs[1])
                        elo = float(commandArgs[2])
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                    await message.channel.send(embed=await setElo(message.author.id, userId, elo))
            if commandArgs[0] == "forcewin":
                await message.channel.send(
                    embed=await score_match(commandArgs, message.author.id, 1, True, True))

    async def on_reaction_add(self, reaction, user):
        embed = reaction.message.embeds[0]
        emoji = reaction.emoji
        print("Emoji Reacted: " + str(emoji))
        if user.bot or self.user.id != reaction.message.author.id:
            return
        if embed.title == "Leaderboard":
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
                else:
                    return
                numEntries = countLeaderboard(0)
                start = max(0, min(start, numEntries))
                fieldValue = generateLeaderboardField(start, count)
                if fieldValue is None or fieldValue == "":
                    return
                embed.set_field_at(0, name="{:d}-{:d}".format(start + 1, start + count),
                                   value=fieldValue)
                await reaction.message.edit(embed=embed)

        if embed.title == "Season High Leaderboard":
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
                else:
                    return
                numEntries = countLeaderboard(0)
                start = max(0, min(start, numEntries))
                fieldValue = generateSeasonHighsField(start, count)
                if fieldValue is None or fieldValue == "":
                    return
                embed.set_field_at(0, name="{:d}-{:d}".format(start + 1, start + count),
                                   value=fieldValue)
                await reaction.message.edit(embed=embed)


client = MyClient()
client.run(config["discord-bot-token"])
