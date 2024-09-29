import discord
from discord import ui, Interaction
from discord._types import ClientT

from model.mmr_leaderboard import LeaderboardEntry
from model.mmr_maps import queryMapsByName, MapEntry


class MapViewEdit(discord.ui.View):
    oldMapName = ""

    def __init__(self, oldMapName):
        self.oldMapName = oldMapName
        super().__init__()

    @discord.ui.button(label="Edit Map", custom_id="EditMapButton", style=discord.ButtonStyle.blurple)
    async def EditMap(self, interaction: discord.Interaction, button: discord.Button):
        mapForm1 = MapForm1(self.oldMapName)
        await interaction.response.send_modal(mapForm1)


class MapViewEditContinue(discord.ui.View):
    incompleteMapEntry = None
    oldMapName = ""

    def __init__(self, incompleteMapEntry, oldMapName):
        self.incompleteMapEntry = incompleteMapEntry
        self.oldMapName = oldMapName
        super().__init__()

    @discord.ui.button(label="Continue Edit Map", custom_id="ContinueEditMapButton", style=discord.ButtonStyle.blurple)
    async def ContinueAddMap(self, interaction: discord.Interaction, button: discord.Button):
        mapForm2 = MapForm2(self.incompleteMapEntry, self.oldMapName)
        await interaction.response.send_modal(mapForm2)


class MapViewAdd(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Add Map", custom_id="AddMapButton", style=discord.ButtonStyle.green)
    async def AddMap(self, interaction: discord.Interaction, button: discord.Button):
        mapForm1 = MapForm1()
        await interaction.response.send_modal(mapForm1)


class MapViewAddContinue(discord.ui.View):
    incompleteMapEntry = None

    def __init__(self, incompleteMapEntry):
        self.incompleteMapEntry = incompleteMapEntry
        super().__init__()

    @discord.ui.button(label="Continue Add Map", custom_id="ContinueAddMapButton", style=discord.ButtonStyle.green)
    async def ContinueAddMap(self, interaction: discord.Interaction, button: discord.Button):
        mapForm2 = MapForm2(self.incompleteMapEntry)
        await interaction.response.send_modal(mapForm2)


class MapViewVote(discord.ui.View):
    mapName = ""

    def __init__(self, mapName):
        self.mapName = mapName
        super().__init__()

    @discord.ui.button(label="Upvote", custom_id="UpvoteButton", style=discord.ButtonStyle.green)
    async def UpVoteMap(self, interaction: discord.Interaction, button: discord.Button):
        leaderboardEntry = LeaderboardEntry(interaction.user.id)
        if leaderboardEntry is None:
            await interaction.response.send_message(f"You need to be registered to play ranked in order to vote.",
                                                    ephemeral=True)
            return
        mapEntries = queryMapsByName(self.mapName, 0, 2)
        if len(mapEntries) == 0:
            await interaction.response.send_message(
                f"{self.mapName} does not exist. Please add the map instead.", ephemeral=True)
            return
        if len(mapEntries) >= 2:
            await interaction.response.send_message(
                f"{self.mapName} has a duplicate. Please remove the duplicate.", ephemeral=True)
            return
        mapEntry = mapEntries[0]
        mapEntry.updateMapVote(interaction.user.id, up_vote=1)
        mapEntry = queryMapsByName(self.mapName, 0, 2)[0]
        await interaction.response.send_message(
            f"You upvoted {self.mapName} ({mapEntry.up_votes}/{mapEntry.up_votes + mapEntry.down_votes})",
            ephemeral=True)

    @discord.ui.button(label="Downvote", custom_id="DownvoteButton", style=discord.ButtonStyle.red)
    async def DownVoteMap(self, interaction: discord.Interaction, button: discord.Button):
        leaderboardEntry = LeaderboardEntry(interaction.user.id)
        if leaderboardEntry is None:
            await interaction.response.send_message(f"You need to be registered to play ranked in order to vote.",
                                                    ephemeral=True)
            return
        mapEntries = queryMapsByName(self.mapName, 0, 2)
        if len(mapEntries) == 0:
            await interaction.response.send_message(
                f"{self.mapName} does not exist. Please add the map instead.", ephemeral=True)
            return
        if len(mapEntries) >= 2:
            await interaction.response.send_message(
                f"{self.mapName} has a duplicate. Please remove the duplicate.", ephemeral=True)
            return
        mapEntry = mapEntries[0]
        mapEntry.updateMapVote(interaction.user.id, down_vote=1)
        mapEntry = queryMapsByName(self.mapName, 0, 2)[0]
        await interaction.response.send_message(
            f"You downvoted {self.mapName} ({mapEntry.up_votes}/{mapEntry.up_votes + mapEntry.down_votes})",
            ephemeral=True)


class MapForm1(ui.Modal):
    name = ui.TextInput(label="Map Name", max_length=64)
    author = ui.TextInput(label="Map Author", max_length=64)
    mediaLink = ui.TextInput(label="Map Media Link", max_length=256, required=False)
    webLink = ui.TextInput(label="Map Web Link", max_length=256, required=False)
    # description = ui.TextInput(label="Map Description", style=discord.TextStyle.paragraph, max_length=256)
    # shortDescription = ui.TextInput(label="Map Short Description", max_length=64)
    tags = ui.TextInput(label="Map Tags. Separated by commas and no spaces.", max_length=256)

    oldMapName = ""
    mapEntry = None

    def __init__(self, oldMapName=""):
        self.oldMapName = oldMapName
        super().__init__(title='Map Form (1/2)')
        if oldMapName != "":
            mapEntries = queryMapsByName(self.oldMapName, 0, 2)
            if len(mapEntries) == 1:
                self.mapEntry = mapEntries[0]
                self.name.default = self.mapEntry.name
                self.author.default = self.mapEntry.author
                self.mediaLink.default = self.mapEntry.link
                self.webLink.default = self.mapEntry.website
                self.tags.default = self.mapEntry.tags

    async def on_submit(self, interaction: Interaction[ClientT], /):
        if self.oldMapName == "":
            mapEntries = queryMapsByName(self.name.value, 0, 1)
            if len(mapEntries) > 0:
                await interaction.response.send_message(
                    f"{self.name.value} is already a registered map. Please edit the map instead.", ephemeral=True)
                return
            self.mapEntry = MapEntry()
            self.mapEntry.name = self.name.value
            self.mapEntry.author = self.author.value
            self.mapEntry.link = self.mediaLink.value
            self.mapEntry.website = self.webLink.value
            # self.mapEntry.description = self.description.value
            # self.mapEntry.short_description = self.shortDescription.value
            self.mapEntry.tags = self.tags.value
            # self.mapEntry.insertMap(self.tags.value)
            await interaction.response.send_message(f"{self.name.value} is almost submitted (1/2).", ephemeral=True,
                                                    view=MapViewAddContinue(self.mapEntry))
            return
        else:
            mapEntries = queryMapsByName(self.oldMapName, 0, 2)
            if len(mapEntries) == 0:
                await interaction.response.send_message(
                    f"{self.oldMapName} does not exist. Please add the map instead.", ephemeral=True)
                return
            if len(mapEntries) >= 2:
                await interaction.response.send_message(
                    f"{self.oldMapName} has a duplicate. Please remove the duplicate.", ephemeral=True)
                return
            self.mapEntry = mapEntries[0]
            self.mapEntry.name = self.name.value
            self.mapEntry.author = self.author.value
            self.mapEntry.link = self.mediaLink.value
            self.mapEntry.website = self.webLink.value
            # newMapEntry.description = self.description.value
            # newMapEntry.short_description = self.shortDescription.value
            self.mapEntry.tags = self.tags.value
            # self.mapEntry.insertMap(self.tags.value)
            await interaction.response.send_message(f"{self.name.value} is almost submitted (1/2).", ephemeral=True,
                                                    view=MapViewEditContinue(self.mapEntry, self.oldMapName))
            return


class MapForm2(ui.Modal):
    description = ui.TextInput(label="Map Description", style=discord.TextStyle.paragraph, max_length=2048,
                               required=False)
    shortDescription = ui.TextInput(label="Map Short Description", max_length=64, required=False)

    mapEntry = None
    oldMapName = ""

    def __init__(self, mapEntry, oldMapName=""):
        self.mapEntry = mapEntry
        self.oldMapName = oldMapName
        super().__init__(title='Map Form (2/2)')
        if oldMapName != "":
            self.description.default = self.mapEntry.description
            self.shortDescription.default = self.mapEntry.short_description

    async def on_submit(self, interaction: Interaction[ClientT], /):
        self.mapEntry.description = self.description.value
        self.mapEntry.short_description = self.shortDescription.value
        if self.oldMapName == "":
            self.mapEntry.insertMap(self.mapEntry.tags)
            await interaction.response.send_message(f"{self.mapEntry.name} has been added.", ephemeral=True)
        else:
            self.mapEntry.updateMap(self.oldMapName)
            await interaction.response.send_message(f"{self.mapEntry.name} has been updated.", ephemeral=True)
