import discord
from threading import Thread

import mysql

from commands.admin_commands import setElo, setBan
from commands.leaderboard_commands import displayLeaderboard, generateLeaderboardField, generateSeasonHighsField
from commands.map_commands import getMaps, getMapsField, delMap, startMapAddSession, isInMapAddSession, \
    getMapAddSession, removeMapAddSession, getMapTags, getTagsField, startMapEditSession, EDIT_NAME, EDIT_AUTHOR, \
    EDIT_LINK, EDIT_DESCRIPTION, EDIT_TAGS
from commands.mmr_commands import score_match, register, stats, gameLimit, decay
from commands.queue_commands import queue, cancel
from controller.pagination import reactWithPaginationEmojis
from model import db
from model.config import refreshConfig, config
from model.mmr_leaderboard import countLeaderboard
from model.mmr_maps import countMaps, countTags

prefix = config["command-prefix"]


class MyClient(discord.Client):

    async def on_ready(self):
        print("Bot Starting")
        connectDb()
        refreshThread = Thread(target=refreshConfig)
        refreshThread.start()

    async def on_message(self, message):
        if not message.content.startswith(prefix) and isinstance(message.channel, discord.channel.DMChannel):
            connectDb()
            if isInMapAddSession(message.author.id):
                session = getMapAddSession(message.author.id)
                if session.isExpired():
                    removeMapAddSession(message.author.id)
                    await message.channel.send("Map add session expired")
                    return
                if session.getCurrentState() == "name":
                    session.addName(message.content)
                    await message.channel.send("Please enter the map's author:")
                elif session.getCurrentState() == "author":
                    session.addAuthor(message.content)
                    await message.channel.send("Please send a link (not an attachment) for the map:")
                elif session.getCurrentState() == "link":
                    session.addLink(message.content)
                    await message.channel.send("Please enter a description for the map:")
                elif session.getCurrentState() == "description":
                    session.addDescription(message.content)
                    await message.channel.send(
                        "Please enter the tags for the map, separated by a comma without spaces:")
                elif session.getCurrentState() == "tags":
                    removeMapAddSession(message.author.id)
                    session.addMapToDatabase(message.content)
                    await message.channel.send(
                        "Map Added to the database! Please verify that it was successfully added, maps with a duplicate name will not be added")
                elif session.getCurrentState() == EDIT_NAME:
                    removeMapAddSession(message.author.id)
                    session.editName(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
                elif session.getCurrentState() == EDIT_AUTHOR:
                    removeMapAddSession(message.author.id)
                    session.editAuthor(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
                elif session.getCurrentState() == EDIT_LINK:
                    removeMapAddSession(message.author.id)
                    session.editLink(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
                elif session.getCurrentState() == EDIT_DESCRIPTION:
                    removeMapAddSession(message.author.id)
                    session.editDescription(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
                elif session.getCurrentState() == EDIT_TAGS:
                    removeMapAddSession(message.author.id)
                    session.editTags(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
            return
        commandArgs = message.content[1:].split(" ")
        commandArgs[0] = commandArgs[0].lower()
        print(commandArgs[0])
        if isinstance(message.channel, discord.channel.DMChannel):
            print("DM Command: " + message.content)
            connectDb()
            if commandArgs[0] == "queue" or commandArgs[0] == "match" or commandArgs[0] == "***hunt***":
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
            if commandArgs[0] == "cancel" or commandArgs[0] == "***sedgebusy***":
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
            connectDb()
            if commandArgs[0] == "help" or commandArgs[0] == "ranked" or commandArgs[0] == "***floranlibrary***":
                embed = discord.embeds.Embed()
                embed.title = "Help"
                embed.description = config["help-text"]
                embed.color = 0x20872c
                await message.channel.send(embed=embed)
            if commandArgs[0] == "tags" or commandArgs[0] == "maptags" or commandArgs[0] == "groups" or commandArgs[0] == "mapgroups" or commandArgs[0] == "***floranclassifications***":
                start = 0
                count = 25
                embed = discord.embeds.Embed()
                embed.title = "Tags Error"
                embed.description = "Error: Please enter a valid number for the tag page"
                if len(commandArgs) == 2:
                    try:
                        start = int(commandArgs[1])
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                tagsEmbed = await message.channel.send(embed=await getMapTags(start, count))
                await reactWithPaginationEmojis(tagsEmbed)
            if commandArgs[0] == "maps" or commandArgs[0] == "***gloomwoods***":
                isRandom = False
                page = 1
                group = "all"
                if len(commandArgs) > 2:
                    isRandom = commandArgs[-1].lower() == "random"
                if len(commandArgs) > 1:
                    if isRandom:
                        group = " ".join(commandArgs[1:len(commandArgs) - 1])
                    else:
                        group = " ".join(commandArgs[1:])
                mapsEmbed = await message.channel.send(embed=await getMaps(group, isRandom, page, 25))
                if mapsEmbed.embeds[0].title.startswith("Maps Found"):
                    await reactWithPaginationEmojis(mapsEmbed)
            if commandArgs[0] == "season":
                pass
            if commandArgs[0] == "stats" or commandArgs[0] == "***hunterpoints***":
                await message.channel.send(embed=await stats(message.author.id))
            if commandArgs[0] == "decay" or commandArgs[0] == "***rot***":
                await message.channel.send(embed=await decay(commandArgs, message.author.id))
            if commandArgs[0] == "gamelimit" or commandArgs[0] == "***sedgegames***":
                await message.channel.send(embed=await gameLimit(commandArgs, message.author.id))
            if commandArgs[0] == "register" or commandArgs[0] == "***sedgehungers***":
                await message.channel.send(embed=await register(message.author.id,
                                                                message.author.name + "#" + str(
                                                                    message.author.discriminator)))
            if commandArgs[0] == "iwin" or commandArgs[0] == "iwon" or commandArgs[0] == "***sedgewins***":
                await message.channel.send(
                    embed=await score_match(commandArgs, "<@" + str(message.author.id) + ">", 1, True, False))
            if commandArgs[0] == "ilose" or commandArgs[0] == "ilost" or commandArgs[0] == "iloss" or commandArgs[0] == "***sedgeinjured***":
                await message.channel.send(
                    embed=await score_match(commandArgs, "<@" + str(message.author.id) + ">", 2, True, False))
            if commandArgs[0] == "leaderboard" or commandArgs[0] == "***sedgestanding***":
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
            if commandArgs[0] == "seasonhighs" or commandArgs[0] == "***sedgeheights***":
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
            connectDb()
            if commandArgs[0] == "addmap":
                await message.channel.send(embed=await startMapAddSession(message.author))
            if commandArgs[0] == "deletemap":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Delete Map Error"
                    embed.description = "Error: Please enter the full valid map name"
                    await message.channel.send(embed=embed)
                    return
                name = " ".join(commandArgs[1:])
                await message.channel.send(embed=await delMap(name))
            if commandArgs[0] == "editmapname":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Edit Map Error"
                    embed.description = "Error: Please enter a map query as an argument"
                    await message.channel.send(embed=embed)
                    return
                arg = " ".join(commandArgs[1:])
                await message.channel.send(embed=await startMapEditSession(message.author, arg, EDIT_NAME))
            if commandArgs[0] == "editmapauthor":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Edit Map Error"
                    embed.description = "Error: Please enter a map query as an argument"
                    await message.channel.send(embed=embed)
                    return
                arg = " ".join(commandArgs[1:])
                await message.channel.send(embed=await startMapEditSession(message.author, arg, EDIT_AUTHOR))
            if commandArgs[0] == "editmaplink":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Edit Map Error"
                    embed.description = "Error: Please enter a map query as an argument"
                    await message.channel.send(embed=embed)
                    return
                arg = " ".join(commandArgs[1:])
                await message.channel.send(embed=await startMapEditSession(message.author, arg, EDIT_LINK))
            if commandArgs[0] == "editmapdescription":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Edit Map Error"
                    embed.description = "Error: Please enter a map query as an argument"
                    await message.channel.send(embed=embed)
                    return
                arg = " ".join(commandArgs[1:])
                await message.channel.send(embed=await startMapEditSession(message.author, arg, EDIT_DESCRIPTION))
            if commandArgs[0] == "editmaptags":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Edit Map Error"
                    embed.description = "Error: Please enter a map query as an argument"
                    await message.channel.send(embed=embed)
                    return
                arg = " ".join(commandArgs[1:])
                await message.channel.send(embed=await startMapEditSession(message.author, arg, EDIT_TAGS))
            if commandArgs[0] == "ban":
                if len(commandArgs) == 2:
                    embed = discord.embeds.Embed()
                    embed.title = "Ban Error"
                    embed.description = "Error: Please enter a valid discord ID (not an @)"
                    try:
                        userId = int(commandArgs[1])
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                    await message.channel.send(embed=await setBan(message.author.id, userId, True))
            if commandArgs[0] == "unban":
                if len(commandArgs) == 2:
                    embed = discord.embeds.Embed()
                    embed.title = "Ban Error"
                    embed.description = "Error: Please enter a valid discord ID (not an @)"
                    try:
                        userId = int(commandArgs[1])
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                    await message.channel.send(embed=await setBan(message.author.id, userId, False))
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
        if user.bot or self.user.id != reaction.message.author.id or len(reaction.message.embeds) == 0:
            return
        embed = reaction.message.embeds[0]
        emoji = reaction.emoji
        print("Emoji Reacted: " + str(emoji))
        connectDb()
        if embed.title == "Leaderboard":
            fieldCount = len(embed.fields)
            if fieldCount > 0:
                field = embed.fields[0]
                splt = field.name.split("-")
                start = int(splt[0]) - 1
                count = int(splt[1]) - start
                numEntries = countLeaderboard(0)
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
                numEntries = countLeaderboard(0)
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
                fieldValue = generateSeasonHighsField(start, count)
                if fieldValue is None or fieldValue == "":
                    return
                embed.set_field_at(0, name="{:d}-{:d}".format(start + 1, start + count),
                                   value=fieldValue)
                await reaction.message.edit(embed=embed)

        if embed.title.startswith("Maps Found"):
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
                fieldValue = getMapsField(tag, start, count)
                if fieldValue is None or fieldValue == "":
                    return
                embed.set_field_at(0, name="{:d}-{:d}".format(start + 1, start + count),
                                   value=fieldValue)
                await reaction.message.edit(embed=embed)
        if embed.title.startswith("Tags Found"):
            fieldCount = len(embed.fields)
            if fieldCount > 0:
                field = embed.fields[0]
                splt = field.name.split("-")
                numEntries = countTags()
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
                fieldValue = getTagsField(start, count)
                if fieldValue is None or fieldValue == "":
                    return
                embed.set_field_at(0, name="{:d}-{:d}".format(start + 1, start + count),
                                   value=fieldValue)
                await reaction.message.edit(embed=embed)


def connectDb():
    if db.connection is None:
        db.connection = mysql.connector.connect(
            host=config["mysql-hostname"],
            database=config["mysql-database"],
            user=config["mysql-user"],
            password=config["mysql-password"],
            autocommit=True
        )
        db.connection.time_zone = '+00:00'
    elif not db.connection.is_connected():
        db.connection.reconnect(10, 1)


client = MyClient()
client.run(config["discord-bot-token"])
