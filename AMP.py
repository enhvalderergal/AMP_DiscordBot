from idlelib.window import add_windows_to_menu
from pprint import pprint
from typing import Union, Dict
from ampapi import *
from ampapi.dataclass import APIParams
from ampapi.instance import AMPInstance, AMPMinecraftInstance
import asyncio
import aiohttp

_params = APIParams(url="http://10.0.200.65:8081", user="EnHvalDerErGal", password="Unitygonk1337")


async def get_instance(instance_name) -> Union[AMPInstance, AMPMinecraftInstance, None]:
    """
    Retrieve the specified instance.
    """
    print(f"🔍 Attempting to get instance: {instance_name}")
    _bridge = Bridge(api_params=_params)
    ADS: AMPControllerInstance = AMPControllerInstance()

    try:
        await ADS.get_instances(format_data=True)
        print("🔍 Successfully retrieved instances.")
    except Exception as e:
        print(f"❌ Error retrieving instances: {e}")
        return None

    # Print all retrieved instances
    print("Instances found:", [instance.friendly_name for instance in ADS.instances])

    for instance in ADS.instances:
        if isinstance(instance, (AMPInstance, AMPMinecraftInstance)):
            if instance.friendly_name == instance_name:
                print(f"✅ Found instance: {instance_name}")
                return instance

    print(f"❌ Instance {instance_name} not found.")
    return None


async def list_instances() -> Dict[str, list]:
    """
    List all available AMP instances.
    """
    _bridge = Bridge(api_params=_params)
    ADS: AMPControllerInstance = AMPControllerInstance()
    await ADS.get_instances(format_data=True)
    instances = [instance.friendly_name for instance in ADS.instances if
                 isinstance(instance, (AMPInstance, AMPMinecraftInstance))]
    return {"instances": instances}


async def get_status(instance: Union[AMPInstance, AMPMinecraftInstance]) -> Dict[str, Union[str, dict]]:
    """
    Get the status of the specified instance and handle errors gracefully.
    """
    try:
        print(f"🔍 Getting status for instance: {instance.friendly_name}")
        status = await instance.get_status(format_data=False)  # Get raw status
        print(f"✅ Status retrieved for {instance.friendly_name}: {status}")
        return status
    except ConnectionError:  # Catching instance offline error
        print(f"❌ ConnectionError: Instance {instance.friendly_name} is unavailable.")
        return {"error": "Instance is offline"}
    except Exception as e:
        print(f"❌ Error retrieving status for {instance.friendly_name}: {e}")
        return {"error": "Failed to retrieve instance status"}


def parse_metrics(status: dict) -> Dict[str, Union[str, int]]:
    """
    Extract relevant metrics from the status dictionary.
    """
    return {
        "cpu_usage": status.get("metrics", {}).get("cpu_usage", {}).get("percent", "Unknown"),
        "memory_usage": status.get("metrics", {}).get("memory_usage", {}).get("percent", "Unknown"),
        "active_users": status.get("metrics", {}).get("active_users", {}).get("raw_value", "Unknown"),
        "uptime": status.get("uptime", "Unknown")
    }


async def get_instance_status(instance_name) -> Dict[str, Union[str, int]]:
    """
    Retrieve and return the status of the specified AMP instance.
    """
    instance = await get_instance(instance_name)
    if instance is None:
        print(f"{instance_name} not found.")
        return {"error": f"Instance {instance_name} not found"}

    status = await get_status(instance)
    if status:
        return parse_metrics(status)
    else:
        return {"error": "Failed to retrieve instance status"}


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
    result = await is_server_running("CS")
    print(result)



if __name__ == "__main__":
    asyncio.run(test())



