
from typing import Union, Dict
from ampapi import *
from ampapi.dataclass import APIParams
from ampapi.instance import AMPInstance, AMPMinecraftInstance
import asyncio
import DataManager
from typing import Dict, List

_params = APIParams(url=DataManager.get_from_config("server_url"), user=DataManager.get_from_config("amp_user"), password=DataManager.get_from_config("amp_password"))


async def get_instance(instance_name) -> Union[AMPInstance, AMPMinecraftInstance, None]:
    """
    Gets an instance based on its name.
    """
    print(f"[DEBUG] Getting instance: {instance_name}")
    _bridge = Bridge(api_params=_params)
    ADS: AMPControllerInstance = AMPControllerInstance()

    await ADS.get_instances(format_data=True)
    instance = next((instance for instance in ADS.instances if instance.friendly_name == instance_name), None)
    return instance




async def fetch_instances() -> Dict[str, List[str]]:
    """
    Fetches all available AMP instances and returns them as a list.
    """
    print("[DEBUG] Fetching instance list.....")
    _bridge = Bridge(api_params=_params)
    ADS: AMPControllerInstance = AMPControllerInstance()

    await ADS.get_instances(format_data=True)
    instances = [instance.friendly_name for instance in ADS.instances if
                 isinstance(instance, (AMPInstance, AMPMinecraftInstance))]

    print(f"[DEBUG] Found instances: {instances}")

    # Fetch ignored instances and ensure it's a list
    ignored_instances = DataManager.get_from_config("ignored_instances", "")
    if isinstance(ignored_instances, str):
        ignored_instances = ignored_instances.split(",") if ignored_instances else []
    elif not isinstance(ignored_instances, list):
        ignored_instances = []

    print(f"[DEBUG] Ignored instances: {ignored_instances}")

    # Remove ignored instances from the list
    filtered_instances = [instance for instance in instances if instance not in ignored_instances]

    print(f"[DEBUG] Filtered instances: {filtered_instances}")

    return filtered_instances





async def get_config_of_instance(instance_name: str) -> Dict[str, Union[str, dict]]:
    """
    Get the configuration of the specified AMP instance.
    """
    try:
        instance = await get_instance(instance_name)
        if instance is None:
            raise ValueError(f"Instance {instance_name} not found.")

        config = await instance.get_config()
        return {"config": config, "instance": instance_name}
    except ValueError as e:
        print(e)
        return {"error": str(e)}
    except Exception as e:
        print(f"Error getting config for {instance_name}: {e}")
        return {"error": f"Failed to get config for {instance_name}: {str(e)}"}







async def start_server(instance_name: str) -> Dict[str, Union[str, dict]]:
    """
    Start the specified AMP instance and its server application.
    """
    instance = await get_instance(instance_name)
    if instance is None:
        print(f"{instance_name} not found.")
        return {"error": f"Instance {instance_name} not found"}

    try:
        await instance.start_instance()  # Start the instance
        await asyncio.sleep(5)  # Wait for the instance to start

        if instance.running:
            await instance.start_application()  # Start the application
            return {"status": "The server is starting", "instance": instance_name}
        else:
            return {"status": "Instance is starting, but is not running yet.", "instance": instance_name}
    except Exception as e:
        print(f"Error starting server application in {instance_name}: {e}")
        return {"error": f"Failed to start server application in {instance_name}"}

async def send_console_message(instance_name: str, message: str) -> Dict[str, Union[str, dict]]:
    """
    Send a console message to the specified AMP instance.
    """
    instance = await get_instance(instance_name)
    if instance is None:
        print(f"{instance_name} not found.")
        return {"error": f"Instance {instance_name} not found"}

    try:
        if instance.running:
            await instance.send_console_message(message)
            return {"status": "Message sent successfully", "instance": instance_name}
        else:
            return {"status": "Instance is not running", "instance": instance_name}
    except Exception as e:
        print(f"Error sending message to {instance_name}: {e}")
        return {"error": f"Failed to send message to {instance_name}"}


async def stop_server(instance_name: str) -> Dict[str, Union[str, dict]]:
    """
    Stop the specified AMP instance's server application.
    """
    instance = await get_instance(instance_name)
    if instance is None:
        print(f"{instance_name} not found.")
        return {"error": f"Instance {instance_name} not found"}

    try:
        if instance.running:
            await instance.stop_application()  # Stop the game server application
            return {"status": "Server application is stopping", "instance": instance_name}
        else:
            return {"status": "Instance is not running", "instance": instance_name}
    except Exception as e:
        print(f"Error stopping server application in {instance_name}: {e}")
        return {"error": f"Failed to stop server application in {instance_name}"}


async def is_server_running(instance_name: str) -> Dict[str, Union[str, bool]]:
    """
    Check if the specified AMP instance is online and if the game server inside it is running.
    """


    try:
        print("Getting instance")
        instance = await get_instance(instance_name)
    except Exception as e:
        print(f"❌ Error while getting status for {instance_name}: {e}")
        return {"error": "Failed to retrieve instance status", "running": False, "status": "unknown"}


    if instance is None:
        print(f"❌ Instance {instance_name} is completely offline or unavailable.")
        return {"error": "Instance is completely offline", "running": False, "status": "offline"}

    try:
        print("Getting status")
        status = await get_status(instance)  # Safely handled inside get_status
        print("failed?")
    except Exception as e:
        print(f"❌ Error while getting status for {instance_name}: {e}")
        return {"error": "Failed to retrieve instance status", "running": False, "status": "unknown"}

    if "error" in status:
        return {"error": "Instance is offline", "running": False, "status": "offline"}

    # Ensure "state" is always treated as a string
    server_state = str(status.get("state", "")).lower()

    if server_state == "running":
        return {"instance": instance_name, "running": True, "status": "online"}

    return {"instance": instance_name, "running": False, "status": "online (server not running)"}


async def test():
    result = await get_config_of_instance("CS")
    print(result)



if __name__ == "__main__":
    asyncio.run(test())



