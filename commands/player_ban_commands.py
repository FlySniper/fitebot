# import discord
# from model.config import config
#
#
# class SimultaneousBansEntry:
#     entryId = 0
#     otherEntryId = 0
#     bans = ""
#
#     def __init__(self, entryId, otherEntryId):
#         self.entryId = entryId
#         self.otherEntryId = otherEntryId
#
#     def setBans(self, bans):
#         self.bans = bans
#
# async def simultaneousBans(author, args):
#     user1 = author.id
#     authorDm = await author.create_dm()
#     if len(args) == 2:
#         user2 = args[1]
#     else:
#         embed = discord.embeds.Embed()
#         embed.title = "Bans Error"
#         embed.color = 0x20872c
#         embed.description = "Error: You must @ one opponent as your argument `%s startbans @opponent#1234`".format(config["command-prefix"])
#         return embed
#     if (user1.startswith("<@") or user1.startswith("<!@")) and user1.endswith(">") and (
#             user2.startswith("<@") or user2.startswith("<!@")) and user2.endswith(">"):
#         id1 = user1.replace("<", "").replace("@", "").replace("!", "").replace(">", "")
#         id2 = user2.replace("<", "").replace("@", "").replace("!", "").replace(">", "")
#         if id1.isnumeric() and id2.isnumeric() and id1 != id2:
pass
