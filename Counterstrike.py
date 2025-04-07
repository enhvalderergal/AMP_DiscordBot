import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import random
import AMP
import asyncio
from typing import Dict, Union

import discord
import random

from DataManager import get_from_config

# List of predefined Counter-Strike maps, including "Edin"
MAP_OPTIONS = [
    app_commands.Choice(name="Dust II", value="de_dust2"),
    app_commands.Choice(name="Inferno", value="de_inferno"),
    app_commands.Choice(name="Mirage", value="de_mirage"),
    app_commands.Choice(name="Nuke", value="de_nuke"),
    app_commands.Choice(name="Train", value="de_train"),
    app_commands.Choice(name="Overpass", value="de_overpass"),
    app_commands.Choice(name="Vertigo", value="de_vertigo"),
    app_commands.Choice(name="Ancient", value="de_ancient"),
    app_commands.Choice(name="Anubis", value="de_anubis"),
    app_commands.Choice(name="Edin", value="de_edin"),
    app_commands.Choice(name="Basalt", value="de_basalt"),
]



# Set of players who have joined the game
players = set()
# Track which map a player voted for
voted_players = {}

# Function to shuffle players into two teams
def shuffleTeams(players_list):
    random.shuffle(players_list)
    n = len(players_list) // 2
    return players_list[:n], players_list[n:]

### ------------------------------------------------------------
### 1️⃣ **PlayCSButton** - Manages joining & team shuffle
### ------------------------------------------------------------
class PlayCSButton(View):
    def __init__(self):
        super().__init__()
        self.update_button_label()

    def update_button_label(self):
        """Update the Join button label with current player count."""
        self.children[0].label = f"Join ({len(players)})"

    @discord.ui.button(label="Join (0)", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handles player joining."""
        user = interaction.user

        if user.id not in players:
            players.add(user.id)  # Add user to players set
            self.update_button_label()  # Update the button label

            # Shuffle teams with current players
            team1, team2 = shuffleTeams(list(players))

            # Update the display message
            await interaction.response.edit_message(content=self.get_message_text(team1, team2), view=self)
        else:
            await interaction.response.send_message("You have already joined!", ephemeral=True)

    def get_message_text(self, team1, team2):
        """Formats the message to display team assignments."""
        if players:
            team1_mentions = ", ".join(f"<@{user_id}>" for user_id in team1)
            team2_mentions = ", ".join(f"<@{user_id}>" for user_id in team2)
            return f"**Team CT:** {team1_mentions}\n**Team T:** {team2_mentions}"
        return "Click the button to join the game!"


### ------------------------------------------------------------
### 2️⃣ **MapVoteView** - Handles voting on maps separately
### ------------------------------------------------------------


# Function to get players in bot.py
def get_players():
    return players

class MapVoteView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.votes = {  # Dictionary to track votes per map
            "de_dust2": 0,
            "de_inferno": 0,
            "de_mirage": 0,
            "de_nuke": 0,
            "de_train": 0,
            "de_overpass": 0,
            "de_vertigo": 0,
            "de_ancient": 0,
            "de_anubis": 0,
            "de_edin": 0,
            "de_basalt": 0,
        }

        # Create buttons dynamically
        for map_name, internal_name in {
            "Dust II": "de_dust2",
            "Inferno": "de_inferno",
            "Mirage": "de_mirage",
            "Nuke": "de_nuke",
            "Train": "de_train",
            "Overpass": "de_overpass",
            "Vertigo": "de_vertigo",
            "Ancient": "de_ancient",
            "Anubis": "de_anubis",
            "Edin": "de_edin",
            "Basalt": "de_basalt",
        }.items():
            button = discord.ui.Button(label=f"{map_name} (0)", style=discord.ButtonStyle.primary, custom_id=internal_name)
            button.callback = self.vote_button  # Set callback for button clicks
            self.add_item(button)

    async def vote_button(self, interaction: discord.Interaction):
        """Handles a vote when a user clicks a button."""
        user = interaction.user
        voted_map = interaction.data["custom_id"]  # Get which button was clicked

        # Check if user has already voted
        if user.id in voted_players:
            await interaction.response.send_message("You have already voted!", ephemeral=True)
            return

        # Register the user's vote
        voted_players[user.id] = voted_map  # Store the user's vote
        self.votes[voted_map] += 1  # Increase vote count for that map
        self.update_button_labels()  # Refresh labels

        # Update the message with new vote counts
        await interaction.response.edit_message(view=self)

        # Check if all players have voted
        if len(voted_players) == len(players):
            await self.end_vote(interaction)

    def update_button_labels(self):
        """Updates button labels with the current vote counts."""
        for button in self.children:
            map_name = button.custom_id
            button.label = f"{map_name.replace('de_', '').title()} ({self.votes[map_name]})"

    async def end_vote(self, interaction: discord.Interaction):
        """Ends the vote when all players have voted, changes the map, and announces the result."""
        winning_map = max(self.votes, key=self.votes.get)  # Get map with most votes
        map_display_name = winning_map.replace('de_', '').title()

        # Attempt to change the map on the server (assuming instance name is "CS")
        result = await change_map(get_from_config(get_from_config("cs_instance_name", "")), winning_map)

        # Build the response message with the result from change_map()
        if "error" in result:
            response_message = (
                f"Voting ended! The selected map is **{map_display_name}**!\n"
                f"⚠️ Error: {result['error']}"
            )
        else:
            response_message = (
                f"Voting ended! The selected map is **{map_display_name}**!\n"
                "✅ Map has been successfully changed on the server!"
            )

        # Edit the original message with the final result
        await interaction.message.edit(content=response_message, view=None)

        # Reset vote tracking for next round
        voted_players.clear()  # Clear the voted players for the next round
        self.votes = {key: 0 for key in self.votes}  # Reset votes per map



class MapVetoView(discord.ui.View):
    def __init__(self, instance_name: str):
        super().__init__()
        self.maps = [
            "de_dust2", "de_inferno", "de_mirage", "de_nuke", "de_train",
            "de_overpass", "de_vertigo", "de_ancient", "de_anubis", "de_edin", "de_basalt"
        ]
        self.players = list(players)  # Convert set to list
        random.shuffle(self.players)  # Shuffle player order
        self.current_player_index = 0

        # Create buttons for map banning
        for map_name in self.maps:
            button = discord.ui.Button(label=f"Ban {map_name.replace('de_', '').title()}",
                                       style=discord.ButtonStyle.danger, custom_id=map_name)
            button.callback = self.ban_button
            self.add_item(button)

    async def ban_button(self, interaction: discord.Interaction):
        """Handles map banning."""
        user = interaction.user

        # Ensure only the correct player can vote
        if user.id != self.players[self.current_player_index]:
            await interaction.response.send_message("It's not your turn to vote!", ephemeral=True)
            return

        # Remove the chosen map
        banned_map = interaction.data["custom_id"]
        self.maps.remove(banned_map)

        # Remove the button from view
        for button in self.children:
            if button.custom_id == banned_map:
                self.remove_item(button)
                break

        # Check if only one map remains (veto complete)
        if len(self.maps) == 1:
            remaining_map = self.maps[0]
            map_display_name = remaining_map.replace('de_', '').title()

            # Call change_map() with the final map
            result = await change_map(self.instance_name, remaining_map)

            # Send result message
            response_message = f"Veto complete! The final map is **{map_display_name}**!\n"
            if "error" in result:
                response_message += f"⚠️ Error: {result['error']}"
            else:
                response_message += "✅ Map has been successfully changed on the server!"

            await interaction.message.edit(content=response_message, view=None)
            return

        # Move to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # Update the message to show whose turn it is
        next_player_mention = f"<@{self.players[self.current_player_index]}>"
        await interaction.message.edit(content=f"**{next_player_mention}, it's your turn to ban a map!**", view=self)


async def start_knife_round(instance_name: str) -> Dict[str, Union[str, dict]]:

    # Define the commands to start a knife round
    commands = [
        "mp_ct_default_melee weapon_knife",  # Set CTs to use knives
        "mp_t_default_melee weapon_knife",  # Set Ts to use knives
        "mp_t_default_secondary \"\"",  # Clear secondary weapon for Ts
        "mp_ct_default_secondary \"\"",  # Clear secondary weapon for CTs
        "mp_ct_default_primary \"\"",  # Clear primary weapon for CTs
        "mp_t_default_primary \"\"",  # Clear primary weapon for Ts
        "mp_roundtime_defuse 6000",  # Set round time (6000 seconds for testing; adjust as needed)
        "mp_warmuptime 0",  # Disable warmup time
        "mp_startmoney 0",  # Set starting money to 0
        "mp_friendlyfire 0",  # Disable friendly fire
        "mp_give_player_c4 0",  # Disable giving C4
        "mp_restartgame 1", #Restarts round
        "say \"Knife round! Fight with knives only!\""  # Inform players
    ]
    # Send each command to the console
    for command in commands:
        response = await AMP.send_console_message(instance_name, command)
        if "error" in response:
            return response  # Return error if any command fails

    return {"status": "Knife round started successfully"}


async def stop_knife_round(instance_name: str) -> Dict[str, Union[str, dict]]:
    # Define the commands to reset settings after knife round
    commands = [
        "mp_ct_default_melee weapon_knife",  # Set CTs to default melee weapon
        "mp_t_default_melee weapon_knife",  # Set Ts to default melee weapon
        "mp_t_default_secondary weapon_glock",  # Set Ts' secondary weapon to Glock
        "mp_ct_default_secondary weapon_usp_silencer",  # Set CTs' secondary weapon to USP
        "mp_roundtime_defuse 1.92",  # Set round time to normal (1.92 minutes)
        "mp_warmuptime 30",  # Set warmup time to normal (30 seconds)
        "mp_startmoney 800",  # Set starting money to normal (800)
        "mp_friendlyfire 1",  # Enable friendly fire (if desired)
        "mp_give_player_c4 1",  # Enable giving C4
        "mp_restartgame 1",  # Restarts round
        "say \"Knife round over!\""  # Inform players
    ]

    # Send each command to the console
    for command in commands:
        response = await AMP.send_console_message(instance_name, command)
        if "error" in response:
            return response  # Return error if any command fails

    return {"status": "Knife round stopped and settings reset successfully"}



async def change_map(instance_name: str, map_name: str) -> Dict[str, Union[str, dict]]:
    """
    Change the map of the counterstrike instance
    """
    instance = await AMP.get_instance(instance_name)
    if instance is None:
        print(f"{instance_name} not found.")
        return {"error": f"Instance {instance_name} not found"}

    try:
        if instance.running:
            command = f"map {map_name}"
            await instance.send_console_message(command)
            return {"status": "Map changed successfully", "instance": instance_name, "map": map_name}
        else:
            return {"status": "Instance is not running", "instance": instance_name}
    except Exception as e:
        print(f"Error changing map for {instance_name}: {e}")
        return {"error": f"Failed to change map for {instance_name}"}
