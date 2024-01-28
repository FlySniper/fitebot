import discord
from model.config import config
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
