import datetime

import discord
from threading import Thread

from discord import app_commands, Interaction
from discord.ext.commands import is_owner, Context

import mysql

from commands.admin_commands import setElo, setBan
from commands.leaderboard_commands import displayLeaderboard, generateLeaderboardField, generateSeasonHighsField, \
    displaySeasonHighs
from commands.map_commands import getMaps, getMapsField, delMap, startMapAddSession, isInMapAddSession, \
    getMapAddSession, removeMapAddSession, getMapTags, getTagsField, startMapEditSession, EDIT_NAME, EDIT_AUTHOR, \
    EDIT_LINK, EDIT_DESCRIPTION, EDIT_TAGS, EDIT_WEBSITE, MAP_MODE_TAGS_OR_NAME, MAP_MODE_NAME, MAP_MODE_TAGS, \
    getMapTagField, getMapNameField, EDIT_SHORT_DESCRIPTION
from commands.mmr_commands import score_match, register, stats, placements, decay
from commands.queue_commands import queue, cancel
from controller.pagination import reactWithPaginationEmojis, arrowEmojiReaction, arrowEmojiReactionMapTag
from controller.seasons import scheduleSeason, getNextSeason
from model import db
from model.config import refreshConfig, config
from model.mmr_leaderboard import countLeaderboard
from model.mmr_maps import countMaps, countTags
from model.mmr_season import querySeason

prefix = config["command-prefix"]
DEBUG_GUILD_IDS = None  # [706545364249083906]


async def getCommandArgs(args):
    commandArgs = args[1:].split(" ")
    commandArgs[0] = commandArgs[0].lower()
    print(commandArgs[0])
    return commandArgs


class MyClient(discord.Client):

    def __init__(self):
        super().__init__(intents=discord.Intents.all())

    async def on_ready(self):
        print("Bot Starting")
        connectDb()
        refreshThread = Thread(target=refreshConfig)
        refreshThread.start()
        scheduleSeasonThread = Thread(target=scheduleSeason)
        scheduleSeasonThread.start()
        print("Bot Started")

    async def setup_hook(self) -> None:
        pass

    async def on_message(self, message):
        if isinstance(message.channel, discord.channel.DMChannel):
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
                    await message.channel.send(
                        "Please send a media link (not an attachment) for the map, or send `skip` to skip:")
                elif session.getCurrentState() == "link":
                    session.addLink(message.content)
                    if config["enable-website-linking"]:
                        await message.channel.send("Please send a URL for the map, or send `skip` to skip:")
                    else:
                        await message.channel.send("Please enter a description for the map:")
                elif session.getCurrentState() == "website" and config["enable-website-linking"]:
                    session.addWebsite(message.content)
                    await message.channel.send("Please enter a description for the map:")
                elif session.getCurrentState() == "description":
                    session.addDescription(message.content)
                    await message.channel.send(
                        "Please enter a short description for the map:")
                elif session.getCurrentState() == "short_description":
                    session.addShortDescription(message.content)
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
                elif session.getCurrentState() == EDIT_WEBSITE:
                    removeMapAddSession(message.author.id)
                    session.editWebsite(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
                elif session.getCurrentState() == EDIT_DESCRIPTION:
                    removeMapAddSession(message.author.id)
                    session.editDescription(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
                elif session.getCurrentState() == EDIT_SHORT_DESCRIPTION:
                    removeMapAddSession(message.author.id)
                    session.editShortDescription(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
                elif session.getCurrentState() == EDIT_TAGS:
                    removeMapAddSession(message.author.id)
                    session.editTags(message.content)
                    await message.channel.send(
                        "Map Edited! Please verify that it was successfully added, maps with a duplicate name will not be added")
                return
        if not message.content.startswith(config["command-prefix"]):
            return
        commandArgs = await getCommandArgs(message.content)
        if isinstance(message.channel, discord.channel.DMChannel):
            print("DM Command: " + message.content)
            connectDb()
            if commandArgs[0] == "sync" and is_owner():
                if DEBUG_GUILD_IDS is None or len(DEBUG_GUILD_IDS) == 0:
                    print(await slashCommand.sync(guild=None))
                else:
                    for guild in DEBUG_GUILD_IDS:
                        print(slashCommand.get_commands(guild=discord.Object(id=guild)))
                        print(await slashCommand.sync(guild=discord.Object(id=guild)))
            if commandArgs[0] == "queue" or commandArgs[0] == "match" or commandArgs[0] == "***hunt***":
                queueTime = 30
                embed = discord.embeds.Embed()
                embed.title = "Queue Error"
                embed.description = "Error: Please enter a number for the time in minutes you would like to queue for"
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
                key = commandArgs[1]
                if key in config["matchmaking"].keys():
                    queueTime = config["matchmaking"][key]["default-queue-time"]
                if len(commandArgs) == 3:
                    try:
                        queueTime = int(commandArgs[2])
                    except ValueError:
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
            if commandArgs[0] == "help" or commandArgs[0] == "***floranlibrary***":
                embed = discord.embeds.Embed()
                embed.title = "Help"
                embed.description = config["help-text"]
                embed.color = 0x20872c
                await message.channel.send(embed=embed)
            if commandArgs[0] == "ranked" or commandArgs[0] == "***floranranked***":
                embed = discord.embeds.Embed()
                embed.title = "Ranked Rules"
                embed.description = config["ranked-text"]
                embed.color = 0x20872c
                await message.channel.send(embed=embed)
            if commandArgs[0] == "tags" or commandArgs[0] == "maptags" or commandArgs[0] == "groups" or commandArgs[
                0] == "mapgroups" or commandArgs[0] == "***floranclassifications***":
                start = 0
                count = 20
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
                embed = await getMaps(group, isRandom, page, 20, MAP_MODE_TAGS_OR_NAME)
                try:
                    mapsEmbed = await message.channel.send(embed=embed)
                    if mapsEmbed.embeds[0].title.startswith("Maps Found"):
                        await reactWithPaginationEmojis(mapsEmbed)
                except discord.errors.HTTPException as ex:
                    await message.channel.send("Error: Map has an invalid media link")
            if commandArgs[0] == "maptag" or commandArgs[0] == "***gloomtags***":
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
                embed = await getMaps(group, isRandom, page, 20, MAP_MODE_TAGS)
                try:
                    mapsEmbed = await message.channel.send(embed=embed)
                    if mapsEmbed.embeds[0].title.startswith("Maps in Tag"):
                        await reactWithPaginationEmojis(mapsEmbed)
                except discord.errors.HTTPException:
                    await message.channel.send("Error: Map has an invalid media link")
            if commandArgs[0] == "mapname" or commandArgs[0] == "***gloomname***":
                page = 1
                group = "all"
                if len(commandArgs) > 1:
                    group = " ".join(commandArgs[1:])
                embed = await getMaps(group, False, page, 20, MAP_MODE_NAME)
                try:
                    mapsEmbed = await message.channel.send(embed=embed)
                    if mapsEmbed.embeds[0].title.startswith("Maps with Name"):
                        await reactWithPaginationEmojis(mapsEmbed)
                except discord.errors.HTTPException:
                    await message.channel.send("Error: Map has an invalid media link")
            if commandArgs[0] == "stats" or commandArgs[0] == "***hunterpoints***":
                await message.channel.send(embed=await stats(message.author.id))
            if commandArgs[0] == "decay" or commandArgs[0] == "***rot***":
                await message.channel.send(embed=await decay(commandArgs, message.author.id))
            if commandArgs[0] == "placements" or commandArgs[0] == "***sedgegames***":
                await message.channel.send(embed=await placements(commandArgs, message.author.id))
            if commandArgs[0] == "register" or commandArgs[0] == "***sedgehungers***":
                await message.channel.send(embed=await register(message.author.id,
                                                                message.author.name + "#" + str(
                                                                    message.author.discriminator)))
            if commandArgs[0] == "iwin" or commandArgs[0] == "iwon" or commandArgs[0] == "***sedgewins***":
                await message.channel.send(
                    embed=await score_match(commandArgs, "<@" + str(message.author.id) + ">", 1, True, False))
            if commandArgs[0] == "ilose" or commandArgs[0] == "ilost" or commandArgs[0] == "iloss" or commandArgs[
                0] == "***sedgeinjured***":
                await message.channel.send(
                    embed=await score_match(commandArgs, "<@" + str(message.author.id) + ">", 2, True, False))
            if commandArgs[0] == "leaderboard" or commandArgs[0] == "***sedgestanding***":
                start = 1
                count = 20
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
                        count = min(int(commandArgs[2]), 20)
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
            if commandArgs[0] == "season" or commandArgs[0] == "***sedgehistory***":
                start = 1
                count = 20
                season = 0
                embed = discord.embeds.Embed()
                embed.title = "Leaderboard Error"
                embed.description = "Error: Please enter a valid number for the leaderboard range"
                if len(commandArgs) == 2:
                    try:
                        season = int(commandArgs[1])
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                elif len(commandArgs) != 1:
                    await message.channel.send(
                        embed=embed)
                    return
                if season != 0:
                    leaderboardMessage = await message.channel.send(
                        embed=await displayLeaderboard(start - 1, count, season=season))
                    await reactWithPaginationEmojis(leaderboardMessage)
                else:
                    embed = discord.embeds.Embed()
                    embed.title = "Current Season"
                    embed.description = f"We are currently on Season {querySeason()}.\nNext season starts on <t:{int(getNextSeason() + (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())}:F>"
                    await message.channel.send(embed=embed)
            if commandArgs[0] == "seasonhighs" or commandArgs[0] == "***sedgeheights***":
                start = 1
                count = 20
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
                        count = min(int(commandArgs[2]), 20)
                    except ValueError:
                        await message.channel.send(
                            embed=embed)
                        return
                elif len(commandArgs) != 1:
                    await message.channel.send(
                        embed=embed)
                    return
                leaderboardMessage = await message.channel.send(
                    embed=await displaySeasonHighs(start - 1, count))
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
            if commandArgs[0] == "editmapwebsite" and config["enable-website-linking"]:
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Edit Map Error"
                    embed.description = "Error: Please enter a map query as an argument"
                    await message.channel.send(embed=embed)
                    return
                arg = " ".join(commandArgs[1:])
                await message.channel.send(embed=await startMapEditSession(message.author, arg, EDIT_WEBSITE))
            if commandArgs[0] == "editmapdescription":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Edit Map Error"
                    embed.description = "Error: Please enter a map query as an argument"
                    await message.channel.send(embed=embed)
                    return
                arg = " ".join(commandArgs[1:])
                await message.channel.send(embed=await startMapEditSession(message.author, arg, EDIT_DESCRIPTION))
            if commandArgs[0] == "editmapshortdescription":
                if len(commandArgs) == 1:
                    embed = discord.embeds.Embed()
                    embed.title = "Edit Map Error"
                    embed.description = "Error: Please enter a map query as an argument"
                    await message.channel.send(embed=embed)
                    return
                arg = " ".join(commandArgs[1:])
                await message.channel.send(embed=await startMapEditSession(message.author, arg, EDIT_SHORT_DESCRIPTION))
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
            await arrowEmojiReaction(embed, emoji, reaction, countLeaderboard(0), generateLeaderboardField)
        if embed.title.startswith("Leaderboard from Season"):
            tempTitle = embed.title
            tempTitle = tempTitle.replace("Leaderboard from Season ", "")
            season = int(tempTitle)
            await arrowEmojiReaction(embed, emoji, reaction, countLeaderboard(0, season=season),
                                     generateLeaderboardField, season=season)
        if embed.title == "Season High Leaderboard":
            await arrowEmojiReaction(embed, emoji, reaction, countLeaderboard(0), generateSeasonHighsField)
        if embed.title.startswith("Maps Found"):
            await arrowEmojiReactionMapTag(embed, emoji, reaction, getMapsField)
        if embed.title.startswith("Maps in Tag"):
            await arrowEmojiReactionMapTag(embed, emoji, reaction, getMapTagField)
        if embed.title.startswith("Maps with Name"):
            await arrowEmojiReactionMapTag(embed, emoji, reaction, getMapNameField)
        if embed.title.startswith("Tags Found"):
            await arrowEmojiReaction(embed, emoji, reaction, countTags(), getTagsField)


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
slashCommand = app_commands.CommandTree(client)


# @slashCommand.command(name="maps",
#                      description="Displays the map pool for the specified query. Can display a random map.",
#                      guild=discord.Object(id=706545364249083906))
async def mapsCommand(interaction: Interaction, query: str = "all", random: bool = False):
    await interaction.response.defer()
    page = 1
    embed = await getMaps(query, random, page, 20, MAP_MODE_TAGS_OR_NAME)
    try:
        mapsEmbed = await interaction.followup.send(embed=embed)
        if mapsEmbed.embeds[0].title.startswith("Maps Found"):
            await reactWithPaginationEmojis(mapsEmbed)
    except discord.errors.HTTPException:
        await interaction.followup.send("Error: Map has an invalid media link")


slashCommand.add_command(discord.app_commands.Command(name="maps",
                                                      description="Displays the map pool for the specified query. Can display a random map.",
                                                      callback=mapsCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def registerCommand(interaction: Interaction):
    await interaction.response.defer()
    await interaction.followup.send(embed=await register(interaction.user.id,
                                                         interaction.user.name + "#" + str(
                                                             interaction.user.discriminator)))


command = discord.app_commands.Command(name="register",
                                       description="Register for ranked matches.",
                                       callback=registerCommand,
                                       guild_ids=DEBUG_GUILD_IDS)
command.guild_only = True
slashCommand.add_command(command)


async def rankedCommand(interaction: Interaction):
    await interaction.response.defer()
    embed = discord.embeds.Embed()
    embed.title = "Ranked Rules"
    embed.description = config["ranked-text"]
    embed.color = 0x20872c
    await interaction.followup.send(embed=embed)


slashCommand.add_command(discord.app_commands.Command(name="ranked",
                                                      description="Shows ranked rules.",
                                                      callback=rankedCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def statsCommand(interaction: Interaction):
    await interaction.response.defer()
    await interaction.followup.send(embed=await stats(interaction.user.id))


slashCommand.add_command(discord.app_commands.Command(name="stats",
                                                      description="View your stats including your mmr.",
                                                      callback=statsCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def placementsCommand(interaction: Interaction):
    await interaction.response.defer()
    await interaction.followup.send(embed=await placements("UNUSED", interaction.user.id))


slashCommand.add_command(discord.app_commands.Command(name="placements",
                                                      description="View how many games you must play until you appear on the leaderboard.",
                                                      callback=placementsCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def leaderboardCommand(interaction: Interaction, page: int = 1, count: int = 20):
    await interaction.response.defer()
    page = max(1, page)
    count = min(max(1, count), 20)
    leaderboardMessage = await interaction.followup.send(
        embed=await displayLeaderboard(page - 1, count))
    await reactWithPaginationEmojis(leaderboardMessage)


slashCommand.add_command(discord.app_commands.Command(name="leaderboard",
                                                      description="Displays the current leaderboard as a chat message.",
                                                      callback=leaderboardCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def seasonHighsCommand(interaction: Interaction, page: int = 1, count: int = 20):
    await interaction.response.defer()
    page = max(1, page)
    count = min(max(1, count), 20)
    leaderboardMessage = await interaction.followup.send(
        embed=await displaySeasonHighs(page - 1, count))
    await reactWithPaginationEmojis(leaderboardMessage)


slashCommand.add_command(discord.app_commands.Command(name="season-highs",
                                                      description="Displays everyone's season high mmr as a leaderboard chat message.",
                                                      callback=seasonHighsCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def mapTagsCommand(interaction: Interaction, page: int = 1):
    await interaction.response.defer()
    page = max(1, page)
    count = 20
    tagsEmbed = await interaction.followup.send(embed=await getMapTags(page, count))
    await reactWithPaginationEmojis(tagsEmbed)


slashCommand.add_command(discord.app_commands.Command(name="map-tags",
                                                      description="Display all the available map tags to search for in the maps query.",
                                                      callback=mapTagsCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def mapTagCommand(interaction: Interaction, tag: str = "all", random: bool = False):
    await interaction.response.defer()
    embed = await getMaps(tag, random, 1, 20, MAP_MODE_TAGS)
    try:
        mapsEmbed = await interaction.followup.send(embed=embed)
        if mapsEmbed.embeds[0].title.startswith("Maps in Tag"):
            await reactWithPaginationEmojis(mapsEmbed)
    except discord.errors.HTTPException:
        await interaction.followup.send("Error: Map has an invalid media link")


slashCommand.add_command(discord.app_commands.Command(name="map-tag",
                                                      description="Display all the available maps with a given tag. Can be random.",
                                                      callback=mapTagCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def mapNameCommand(interaction: Interaction, name: str = "all"):
    await interaction.response.defer()
    embed = await getMaps(name, False, 1, 20, MAP_MODE_NAME)
    try:
        mapsEmbed = await interaction.followup.send(embed=embed)
        if mapsEmbed.embeds[0].title.startswith("Maps with Name"):
            await reactWithPaginationEmojis(mapsEmbed)
    except discord.errors.HTTPException:
        await interaction.followup.send("Error: Map has an invalid media link")


slashCommand.add_command(discord.app_commands.Command(name="map-name",
                                                      description="Display all the available maps with a given name.",
                                                      callback=mapNameCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def iwinCommand(interaction: Interaction, name: discord.Member):
    await interaction.response.defer()
    await interaction.followup.send(
        embed=await score_match(["", "<@" + str(name.id) + ">"], "<@" + str(interaction.user.id) + ">", 1, True, False))
    if interaction.channel:
        await interaction.channel.send("<@" + str(name.id) + ">")


command = discord.app_commands.Command(name="i-win",
                                       description="Type /i-win @opponent#1234 if you won against your opponent in a ranked match.",
                                       callback=iwinCommand,
                                       guild_ids=DEBUG_GUILD_IDS)
command.guild_only = True
slashCommand.add_command(command)


async def iloseCommand(interaction: Interaction, name: discord.Member):
    await interaction.response.defer()
    await interaction.followup.send(
        embed=await score_match(["", "<@" + str(name.id) + ">"], "<@" + str(interaction.user.id) + ">", 2, True, False))

    if interaction.channel:
        await interaction.channel.send("<@" + str(name.id) + ">")


command = discord.app_commands.Command(name="i-lose",
                                       description="Type /i-lose @opponent#1234 if you lost against your opponent in a ranked match.",
                                       callback=iloseCommand,
                                       guild_ids=DEBUG_GUILD_IDS)
command.guild_only = True
slashCommand.add_command(command)


async def helpCommand(interaction: Interaction):
    await interaction.response.defer()
    embed = discord.embeds.Embed()
    embed.title = "Help"
    embed.description = config["help-text"]
    embed.color = 0x20872c
    await interaction.followup.send(embed=embed)


slashCommand.add_command(discord.app_commands.Command(name="help",
                                                      description="Shows a list of commands.",
                                                      callback=helpCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))


async def seasonCommand(interaction: Interaction, season: int | None = None):
    await interaction.response.defer()
    start = 1
    count = 20
    if not (season is None):
        leaderboardMessage = await interaction.followup.send(
            embed=await displayLeaderboard(start - 1, count, season=season))
        await reactWithPaginationEmojis(leaderboardMessage)
    else:
        embed = discord.embeds.Embed()
        embed.title = "Current Season"
        embed.description = f"We are currently on Season {querySeason()}.\nNext season starts on <t:{int(getNextSeason() + (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds())}:F>"
        await interaction.followup.send(embed=embed)


slashCommand.add_command(discord.app_commands.Command(name="season",
                                                      description="View the current season. Use /season <number> to see the leaderboard for that season.",
                                                      callback=seasonCommand,
                                                      guild_ids=DEBUG_GUILD_IDS))

client.run(config["discord-bot-token"])
