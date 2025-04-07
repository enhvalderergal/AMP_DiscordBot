import json

CONFIG_FILE = "config.json"


## Function to load the config file
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            print("[DEBUG] Config loaded successfully:", config)  # Debug message
            return config
    except FileNotFoundError:
        print("[DEBUG] Config file not found, using empty config.")  # Debug message
        return {}
    except json.JSONDecodeError:
        print("[DEBUG] Error reading config file, using empty config.")  # Debug message
        return {}

# Function to get a value from config with a default fallback
def get_from_config(key, default=None):
    config = load_config()
    value = config.get(key, default)
    return value
