import discord

from client import MyClient
from controller.mmr_calculations import mmr_calc
from model.mmr_leaderboard import LeaderboardEntry


async def score_match(args, client, user1, victory, updateStats):
    if len(args) == 3:
        user1 = args[1]
        user2 = args[2]
    elif len(args) == 2:
        user2 = args[1]
    else:
        embed = discord.embeds.Embed()
        embed.title = "Manual Entry Results"
        embed.color = "#20872c"
        embed.description = "Error: You must @ one person as your argument `!iwin|!ilost @opponent#1234`"
        return embed
    if (user1.startsWith("<@") or user1.startsWith("<!@")) and user1.endsWith(">") and (user2.startsWith("<@") or user2.startsWith("<!@")) and user2.endsWith(">"):
        id1 = user1.replace("<", "").replace("@", "").replace("!", "").replace(">", "")
        id2 = user2.replace("<", "").replace("@", "").replace("!", "").replace(">", "")
        if id1.isnumeric() and id2.isnumeric():
            mmr_calc(MyClient.config, LeaderboardEntry(int(user1)), LeaderboardEntry(int(user2)), victory, updateStats)
        else:
            pass # Error handling here
    else:
        pass # Error handling here
