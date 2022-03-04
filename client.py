import discord
from threading import Thread
from time import sleep

import mysql
import yaml

from commands.mmr_commands import score_match, register
from model import db

prefix = "?"


def refresh():
    while True:
        sleep(60 * 60 * 1)  # One hour
        MyClient.config = openConfig()


def openConfig():
    with open("config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config


class MyClient(discord.Client):
    config = openConfig()

    async def on_ready(self):
        print("Bot Starting")
        db.connection = mysql.connector.connect(
            host=self.config["mysql-hostname"],
            database=self.config["mysql-database"],
            user=self.config["mysql-user"],
            password=self.config["mysql-password"]
        )
        refreshThread = Thread(target=refresh)
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
        if message.channel.id in self.config["command-channels"] or "all" in self.config["command-channels"]:
            if commandArgs[0] == "maps":
                pass
            if commandArgs[0] == "season":
                pass
            if commandArgs[0] == "stats":
                pass
            if commandArgs[0] == "decay":
                pass
            if commandArgs[0] == "gamelimit":
                pass
            if commandArgs[0] == "register":
                await message.channel.send(embed=await register(self, message.author.id, message.author.tag))
            if commandArgs[0] == "iwin" or commandArgs[0] == "iwon":
                await message.channel.send(embed=await score_match(commandArgs, self, "<@" + str(message.author.id) + ">", 1, True, False))
            if commandArgs[0] == "ilose" or commandArgs[0] == "ilost" or commandArgs[0] == "iloss":
                await message.channel.send(embed=await score_match(commandArgs, self, "<@" + str(message.author.id) + ">", 2, True, False))
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
        if message.channel.id in self.config["admin-channels"]:
            if commandArgs[0] == "ban":
                pass
            if commandArgs[0] == "unban":
                pass
            if commandArgs[0] == "setelo":
                pass
            if commandArgs[0] == "forcewin":
                await message.channel.send(embed=await score_match(commandArgs, self, "<@" + str(message.author.id) + ">", 1, True, True))


client = MyClient()
client.run(MyClient.config["discord-bot-token"])
