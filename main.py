#!/usr/bin/env -S python3
import subprocess
import argparse
import json
import warnings
import os
import venv
import DataManager

CONFIG_FILE = "config.json"
VENV_DIR = "env"  # Directory for the virtual environment

#Need to be done
#Defineing BeamMP Maps (Default is there normally)

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


# Function to create a virtual environment if it doesn't exist and install necessary packages
def create_virtualenv():
    if not os.path.exists(VENV_DIR):
        print("Virtual environment not found. Creating a new one...")
        venv.create(VENV_DIR, with_pip=True)
    else:
        print("Virtual environment already exists.")

    # Install required packages in the virtual environment
    print("Installing necessary packages (discord, cc-ampapi, dataclass_wizard, typing_extensions, and pyotp)...")
    pip_install("discord")
    pip_install("cc-ampapi")
    pip_install("dataclass_wizard")
    pip_install("typing_extensions")
    pip_install("pyotp")


# Function to run pip install in the virtual environment
def pip_install(package):
    # Adjust path for Windows if necessary:
    if os.name == "nt":
        python_exec = os.path.join(VENV_DIR, "Scripts", "python")
    else:
        python_exec = os.path.join(VENV_DIR, "bin", "python")
    subprocess.run([python_exec, "-m", "pip", "install", package])


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
    print("Config updated! Discord token updated")

# Save updated config
save_config(config)
print("Config updated successfully!")

# Create virtual environment and install dependencies (including cc-ampapi, dataclass_wizard, typing_extensions, and pyotp)
create_virtualenv()

# Check if discord token exists and run bot.py using the virtual environment's python
if DataManager.get_from_config("discord_token") != "":
    print("The discord token exists")
    if os.name == "nt":
        python_exec = os.path.join(VENV_DIR, "Scripts", "python")
    else:
        python_exec = os.path.join(VENV_DIR, "bin", "python")
    subprocess.run([python_exec, "bot.py"])
    print("Program successfully started")
else:
    warnings.warn("Warning⚠️: NO TOKEN GIVEN FOR YOUR DISCORD BOT")



#Need to do
#Value for ignored servers