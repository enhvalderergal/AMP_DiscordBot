import discord
from discord import app_commands
from discord.ext import commands
import AMP
import Counterstrike
import DataManager
from AMP import fetch_instances
from DataManager import get_from_config

# Create bot instance with intents
intents = discord.Intents.default()
intents.reactions = True  # Enable reaction tracking
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)




# If the default == "" then commands from that server should be ignored
ArkInstanceName = DataManager.get_from_config("ark_instance_name", "")
CounterstrikeInstanceName = DataManager.get_from_config("cs_instance_name", "")
MinecraftInstanceName = DataManager.get_from_config("mine_instance_name", "")
BeamMPInstanceName = DataManager.get_from_config("beam_instance_name", "")







@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync error: {e}")

# ============================
# Ark
@bot.tree.command(name="ark_cleardinoes", description="Wipe out wild dinos with style!")
async def cleardinoes(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    instance = await AMP.get_instance(ArkInstanceName)

    if instance.running:
        command = "destroywilddinos"
        result = await AMP.send_console_message(ArkInstanceName, command)
        success_message = "🔥 **Wild Dino Purge Activated!"
        await interaction.followup.send(success_message, ephemeral=True)
    else:
        offline_message = "🚫 **Oops!** The Ark server is offline. Please start the game server"
        await interaction.followup.send(offline_message, ephemeral=True)


# ============================
# BeamMp

@bot.tree.command(name="beam_change_map", description="Change the map on the BeamNG server.")
async def change_beam_map(interaction: discord.Interaction, map_name: str):
    await interaction.response.defer(thinking=True, ephemeral=True)

    instance = await AMP.get_instance(BeamMPInstanceName)

    if instance.running:
        command = f"freeroam.loadLevel('{map_name}')"
        result = await AMP.send_console_message(BeamMPInstanceName, command)
        success_message = f"🌍 **Map changed to:** `{map_name}`!"
        await interaction.followup.send(success_message, ephemeral=True)
    else:
        offline_message = "🚫 **Oops!** The BeamNG server is offline. Please start the game server."
        await interaction.followup.send(offline_message, ephemeral=True)


@change_beam_map.autocomplete("map_name")
async def map_autocomplete(interaction: discord.Interaction, current: str):

    maps_list = DataManager.get_from_config("beam_maps").split(",")
    options = [
        app_commands.Choice(name=map_name, value=map_name) for map_name in maps_list
    ]

    # Filter options based on the current input
    return [option for option in options if current.lower() in option.name.lower()]


# ============================
# Minecraft
@bot.tree.command(name="whitelist", description="Adds player to whitelist")
async def minecraft_whitelist(interaction: discord.Interaction, username: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    instance = await AMP.get_instance(MinecraftInstanceName)

    if instance.running:
        Command = f"whitelist add {username}"
        result = await AMP.send_console_message(MinecraftInstanceName, Command)
        await interaction.followup.send(result, ephemeral=True)
    else:
        await interaction.followup.send("⚠️ The Minecraft server is offline, and the game server is not running.",
                                        ephemeral=True)

@bot.tree.command(name="console_channel", description="Sets a channel to enter minecraft console commands")
async def minecraft_console_channel(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send("this feature has not been implimented yet", ephemeral=True)

@bot.tree.command(name="chat_channel", description="Sets a channel to a text channel between minecraft and discord")
async def minecraft_chat_channel(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send("this feature has not been implimented yet", ephemeral=True)

@bot.tree.command(name="who_is_online", description="Gives an overview of current online players")
async def minecraft_online(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send("this feature has not been implimented yet", ephemeral=True)


# ============================
# Counterstrike

# Command to start the Counter-Strike game and set up the join button
@bot.tree.command(name="play_counterstrike", description="Starts the Counter-Strike game")
async def play_cs(interaction: discord.Interaction):
    """Starts the Counter-Strike game and sets up the button for players to join."""
    await interaction.response.defer(thinking=True)
    view = Counterstrike.PlayCSButton()  # Create the button view
    await interaction.followup.send(content="Click to join the game!", view=view)

# Command to shuffle teams manually
@bot.tree.command(name="shuffle_teams", description="Shuffles teams")
async def cs_shuffle(interaction: discord.Interaction):
    """Command to manually shuffle teams and display the shuffled teams."""
    if len(Counterstrike.players) < 1:
        await interaction.response.send_message("Not enough players to shuffle!", ephemeral=True)
        return

    # Shuffle teams with current players
    team1, team2 = Counterstrike.shuffleTeams(list(Counterstrike.players))

    # Generate shuffled message
    shuffled_message = f"**Shuffled Teams:**\n**Team CT:** " + ", ".join(f"<@{user_id}>" for user_id in team1) + \
        f"\n**Team T:** " + ", ".join(f"<@{user_id}>" for user_id in team2)

    # Send message showing the shuffled teams
    await interaction.response.send_message(shuffled_message, ephemeral=True)


@bot.tree.command(name="start_knife_round", description="Starts knife round")
async def cs_start_kniferound(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    result = await Counterstrike.start_knife_round("CS")
    await interaction.followup.send(result["status"], ephemeral=True)

@bot.tree.command(name="stop_knife_round", description="starts knife round")
async def cs_stop_kniferound(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    result = await Counterstrike.stop_knife_round("CS")
    await interaction.followup.send(result["status"], ephemeral=True)




@bot.tree.command(name="counterstrike_info", description="Gets the match info")
async def cs_info(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send("this feature has not been implimented yet", ephemeral=True)

@bot.tree.command(name="counterstrike_map", description="Change the map of Counter-Strike")
async def cs_change_map(interaction: discord.Interaction, map_name: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    await Counterstrike.change_map(CounterstrikeInstanceName, map_name)
    await interaction.followup.send(f"Changed map to {map_name}", ephemeral=True)

@cs_change_map.autocomplete("map_name")
async def map_autocomplete(interaction: discord.Interaction, current: str):
    options = Counterstrike.MAP_OPTIONS

    # Return the options that match the current input
    return [option for option in options if current.lower() in option.name.lower()]


@bot.tree.command(name="counterstrike_vote", description="Start a vote on which Counter-Strike map to play")
async def cs_vote(interaction: discord.Interaction):
    """Starts the vote and sends buttons for each map."""
    players = Counterstrike.get_players()  # Access the shared players set

    if not players:
        await interaction.response.send_message("No players have joined the game! Use `/play_counterstrike` first.",
                                                ephemeral=True)
        return

    players.add(interaction.user.id)  # Automatically add the user who invoked the command

    view = Counterstrike.MapVoteView()  # Use the imported class
    await interaction.response.send_message("Please vote for a map below:", view=view)


@bot.tree.command(name="counterstrike_vote_veto", description="Create a veto vote between the maps")
async def cs_vote_veto(interaction: discord.Interaction, instance_name: str):
    await interaction.response.defer(thinking=True)

    if len(Counterstrike.players) < 2:
        await interaction.followup.send("At least two players must join the game to start vetoing.")
        return

    # Pass the instance_name when creating the view
    view = Counterstrike.MapVetoView(instance_name=instance_name)
    await interaction.followup.send("Start banning maps! Players take turns vetoing.", view=view)



# ============================
# General server manipulation

@bot.tree.command(name="start")
@app_commands.describe(instance_name="Choose the server you want to start")
async def start(interaction: discord.Interaction, instance_name: str):
    await interaction.response.defer(thinking=True)
    result = await AMP.start_server(instance_name)
    await interaction.followup.send(result["status"])

@bot.tree.command(name="stop")
@app_commands.describe(instance_name="Choose the server you want to start")
async def stop(interaction: discord.Interaction, instance_name: str):
    await interaction.response.defer(thinking=True)
    result = await AMP.stop_server(instance_name)
    await interaction.followup.send(result["status"])

@bot.tree.command(name="status")
@app_commands.describe(instance_name="Choose the server you want data from")
async def status(interaction: discord.Interaction, instance_name: str):
    status = await AMP.get_instance_status(instance_name)
    formatted_Value = (
        f"System Information:\n"
        f"CPU Usage: {status['cpu_usage']}%\n"
        f"Memory Usage: {status['memory_usage']} MB\n"
        f"Active Users: {status['active_users']}\n"
        f"Uptime: {status['uptime']}"
    )
    await interaction.response.send_message(formatted_Value)

# Autocomplete for instance names
@status.autocomplete("instance_name")
@start.autocomplete("instance_name")
@stop.autocomplete("instance_name")
async def status_autocomplete(interaction: discord.Interaction, current: str):
    # Fetch instances asynchronously
    instances = await fetch_instances()

    # Create choices dynamically based on fetched instances
    options = [
        app_commands.Choice(name=instance, value=instance) for instance in instances
    ]

    # Filter options based on the current input
    return [option for option in options if current.lower() in option.name.lower()]


# Run the bot with the token
bot.run(get_from_config("discord_token"))
