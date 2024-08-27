import discord
import random
from model.memory import bans, bans_channel


async def simultaneousBans(client: discord.Client, channel_id: int, player: int, opponent_id: int):
    player_obj = await client.fetch_user(player)
    opponent_obj = await client.fetch_user(opponent_id)
    player_dm = await player_obj.create_dm()
    opponent_dm = await opponent_obj.create_dm()
    if player_dm is not None and opponent_dm is not None:
        embed = discord.embeds.Embed()
        embed.title = "Start Bans"
        embed.description = "Please enter your bans separated by a comma"
        await player_dm.send(embed=embed)
        await opponent_dm.send(embed=embed)
        bans[player] = opponent_id
        bans[opponent_id] = player
        bans_channel[player] = channel_id
        bans_channel[opponent_id] = channel_id


async def coin(player1: int, player2: int | None):
    value = random.randint(0, 1) == 1
    message = "Heads" if value else "Tails"
    if player2 is None:
        embed = discord.embeds.Embed()
        embed.title = f"{message}!"
        embed.description = f"<@{player1}> flips a coin and it lands on **{message}!**"
        embed.color = 0x20872c
        return embed
    else:
        winning_player = player1 if value else player2
        losing_player = player2 if value else player1
        embed = discord.embeds.Embed()
        embed.title = f"{message}!"
        embed.description = f"<@{winning_player}> called {message} and won the coin flip against <@{losing_player}>!"
        embed.color = 0x20872c
        return embed
