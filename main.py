#!/usr/bin/env python3
import subprocess
import argparse
import json
import warnings
import DataManager




CONFIG_FILE = "config.json"

# Load the existing config file or create one if it does not exist
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Saves the config to a file
def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

# Argument parser
parser = argparse.ArgumentParser(description="Update the config.json with the new parameters")
parser.add_argument('--minecraft_instance_name', type=str, help='The AMP name of your minecraft instance')
parser.add_argument('--cs_instance_name', type=str, help='The AMP name of your Counterstrike II instance')
parser.add_argument('--ark_instance_name', type=str, help='The AMP name of your Ark instance')
parser.add_argument('--beam_instance_name', type=str, help='The AMP name of your BeamMp instance')

parser.add_argument('--discord_token', type=str, help='Your discord bot TOKEN')

args = parser.parse_args()


# Load existing config
config = load_config()

# Update config only if arguments are provided
if args.minecraft_instance_name:
    config["mine_instance_name"] = args.minecraft_instance_name
    print(f"Config updated! Minecraft instance name = {args.minecraft_instance_name}")
if args.cs_instance_name:
    config["cs_instance_name"] = args.cs_instance_name
    print(f"Config updated! Counterstrike instance name = {args.cs_instance_name}")
if args.ark_instance_name:
    config["ark_instance_name"] = args.ark_instance_name
    print(f"Config updated! Ark instance name = {args.ark_instance_name}")
if args.beam_instance_name:
    config["beam_instance_name"] = args.beam_instance_name
    print(f"Config updated! BeamMp instance name = {args.beam_instance_name}")
if args.discord_token:
    config["discord_token"] = args.discord_token
    print(f"Config updated! Discord token updated name")

# Save updated config
save_config(config)
print("Starting program...")
print("Config updated successfully!")

if DataManager.get_from_config("discord_token") != "":
    print("The discord token exists")
    subprocess.run(["python", "bot.py"])
    print("Program successfully started")
else:
    warnings.warn("Warning⚠️: NO TOKEN GIVEN FOR YOUR DISCORD BOT")
