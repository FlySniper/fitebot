import discord

from model.config import config


async def reactWithPaginationEmojis(message):
    await message.add_reaction("\u23EA")
    await message.add_reaction("\u2B05")
    await message.add_reaction("\u27A1")
    await message.add_reaction("\u23E9")
