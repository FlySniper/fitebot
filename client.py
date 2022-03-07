import discord
from threading import Thread

import mysql

from commands.mmr_commands import score_match, register, stats
from model import db
from model.config import refreshConfig, config

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
        refreshThread = Thread(target=refreshConfig)
        refreshThread.start()

    async def on_message(self, message):
        if not message.content.startswith(prefix):
            return
        commandArgs = message.content[1:].split(" ")
        print(commandArgs[0])
        if message.channel.type == "dm":
            print("DM Command: " + message.content)
            if commandArgs[0] == "queue":
                pass
            if commandArgs[0] == "iban":
                pass
            if commandArgs[0] == "stopbans":
                pass
            if commandArgs[0] == "accept":
                pass
            if commandArgs[0] == "cancel":
                pass
        if message.channel.id in config["command-channels"] or "all" in config["command-channels"]:
            if commandArgs[0] == "maps":
                pass
            if commandArgs[0] == "season":
                pass
            if commandArgs[0] == "stats":
                await message.channel.send(embed=await stats(self, message.author.id))
            if commandArgs[0] == "decay":
                pass
            if commandArgs[0] == "gamelimit":
                pass
            if commandArgs[0] == "register":
                await message.channel.send(embed=await register(self, message.author.id, message.author.name+"#"+str(message.author.discriminator)))
            if commandArgs[0] == "iwin" or commandArgs[0] == "iwon":
                await message.channel.send(
                    embed=await score_match(commandArgs, self, "<@" + str(message.author.id) + ">", 1, True, False))
            if commandArgs[0] == "ilose" or commandArgs[0] == "ilost" or commandArgs[0] == "iloss":
                await message.channel.send(
                    embed=await score_match(commandArgs, self, "<@" + str(message.author.id) + ">", 2, True, False))
            if commandArgs[0] == "help" or commandArgs[0] == "ranked":
                pass
            if commandArgs[0] == "leaderboard":
                pass
            if commandArgs[0] == "seasonhighs":
                pass
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
                pass
            if commandArgs[0] == "forcewin":
                await message.channel.send(
                    embed=await score_match(commandArgs, self, message.author.id, 1, True, True))


client = MyClient()
client.run(config["discord-bot-token"])
