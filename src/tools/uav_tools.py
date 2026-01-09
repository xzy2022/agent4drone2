"""
UAV Control Tools
Wraps the UAV API client as LangChain tools using @tool decorator
All tools accept JSON string input for consistent parameter handling
"""
from langchain.tools import tool
from src.api_client import UAVAPIClient
import json


class UAVToolsRegistry:
    """
    Registry for UAV control tools

    This class organizes tools into categories for better management
    and provides a clean interface for tool retrieval.
    """

    def __init__(self, client: UAVAPIClient):
        self.client = client
        self._tools = {}
        self._register_all_tools()

    def _register_all_tools(self):
        """Register all UAV tools"""
        # Information gathering tools
        self._tools['list_drones'] = self._create_list_drones()
        self._tools['get_session_info'] = self._create_get_session_info()
        self._tools['get_task_progress'] = self._create_get_task_progress()
        self._tools['get_weather'] = self._create_get_weather()
        self._tools['get_drone_status'] = self._create_get_drone_status()
        self._tools['get_nearby_entities'] = self._create_get_nearby_entities()

        # Flight control tools
        self._tools['take_off'] = self._create_take_off()
        self._tools['land'] = self._create_land()
        self._tools['move_to'] = self._create_move_to()
        self._tools['move_towards'] = self._create_move_towards()
        self._tools['change_altitude'] = self._create_change_altitude()
        self._tools['hover'] = self._create_hover()
        self._tools['rotate'] = self._create_rotate()
        self._tools['return_home'] = self._create_return_home()

        # Utility tools
        self._tools['set_home'] = self._create_set_home()
        self._tools['calibrate'] = self._create_calibrate()
        self._tools['take_photo'] = self._create_take_photo()
        self._tools['charge'] = self._create_charge()

        # Communication tools
        self._tools['send_message'] = self._create_send_message()
        self._tools['broadcast'] = self._create_broadcast()

    def get_tool(self, name: str):
        """Get a specific tool by name"""
        return self._tools.get(name)

    def get_all_tools(self) -> list:
        """Get all registered tools"""
        return list(self._tools.values())

    def get_tool_names(self) -> list:
        """Get all tool names"""
        return list(self._tools.keys())

    # ========== Tool Creation Methods ==========

    def _create_list_drones(self):
        @tool
        def list_drones() -> str:
            """List all available drones in the current session with their status, battery level, and position.
            Use this to see what drones are available before trying to control them.

            No input required."""
            try:
                drones = self.client.list_drones()
                return json.dumps(drones, indent=2)
            except Exception as e:
                return f"Error listing drones: {str(e)}"
        return list_drones

    def _create_get_session_info(self):
        @tool
        def get_session_info() -> str:
            """Get current session information including task type, statistics, and status.
            Use this to understand what mission you need to complete.

            No input required."""
            try:
                session = self.client.get_current_session()
                return json.dumps(session, indent=2)
            except Exception as e:
                return f"Error getting session info: {str(e)}"
        return get_session_info

    def _create_get_task_progress(self):
        @tool
        def get_task_progress() -> str:
            """Get mission task progress including completion percentage and status.
            Use this to track mission completion and see how close you are to finishing.

            No input required."""
            try:
                progress = self.client.get_task_progress()
                return json.dumps(progress, indent=2)
            except Exception as e:
                return f"Error getting task progress: {str(e)}"
        return get_task_progress

    def _create_get_weather(self):
        @tool
        def get_weather() -> str:
            """Get current weather conditions including wind speed, visibility, and weather type.
            Check this before takeoff to ensure safe flying conditions.

            No input required."""
            try:
                weather = self.client.get_weather()
                return json.dumps(weather, indent=2)
            except Exception as e:
                return f"Error getting weather: {str(e)}"
        return get_weather

    def _create_get_drone_status(self):
        @tool
        def get_drone_status(input_json: str) -> str:
            """Get detailed status of a specific drone including position, battery, heading, and visited targets.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)

            Example: {{"drone_id": "drone-001"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')

                if not drone_id:
                    return "Error: drone_id is required"

                status = self.client.get_drone_status(drone_id)
                return json.dumps(status, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\"}}"
            except Exception as e:
                return f"Error getting drone status: {str(e)}"
        return get_drone_status

    def _create_get_nearby_entities(self):
        @tool
        def get_nearby_entities(input_json: str) -> str:
            """Get drones, targets, and obstacles near a specific drone (within its perception radius).

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)

            Example: {{"drone_id": "drone-001"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')

                if not drone_id:
                    return "Error: drone_id is required"

                nearby = self.client.get_nearby_entities(drone_id)
                return json.dumps(nearby, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\"}}"
            except Exception as e:
                return f"Error getting nearby entities: {str(e)}"
        return get_nearby_entities

    def _create_take_off(self):
        @tool
        def take_off(input_json: str) -> str:
            """Command a drone to take off to a specified altitude.
            Drone must be on ground (idle or ready status).

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)
            - altitude: Target altitude in meters (optional, default: 10.0)

            Example: {{"drone_id": "drone-001", "altitude": 15.0}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                altitude = params.get('altitude', 10.0)

                if not drone_id:
                    return "Error: drone_id is required"

                result = self.client.take_off(drone_id, altitude)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\", \"altitude\": 15.0}}"
            except Exception as e:
                return f"Error during takeoff: {str(e)}"
        return take_off

    def _create_land(self):
        @tool
        def land(input_json: str) -> str:
            """Command a drone to land at its current position.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)

            Example: {{"drone_id": "drone-001"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')

                if not drone_id:
                    return "Error: drone_id is required"

                result = self.client.land(drone_id)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\"}}"
            except Exception as e:
                return f"Error during landing: {str(e)}"
        return land

    def _create_move_to(self):
        @tool
        def move_to(input_json: str) -> str:
            """Move a drone to specific 3D coordinates (x, y, z).
            Always check for collisions first using check_path_collision.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)
            - x: Target X coordinate in meters (required)
            - y: Target Y coordinate in meters (required)
            - z: Target Z coordinate (altitude) in meters (required)

            Example: {{"drone_id": "drone-001", "x": 100.0, "y": 50.0, "z": 20.0}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                x = params.get('x')
                y = params.get('y')
                z = params.get('z')

                if not drone_id:
                    return "Error: drone_id is required"
                if x is None or y is None or z is None:
                    return "Error: x, y, and z coordinates are required"

                result = self.client.move_to(drone_id, x, y, z)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\", \"x\": 100.0, \"y\": 50.0, \"z\": 20.0}}"
            except Exception as e:
                return f"Error moving drone: {str(e)}"
        return move_to

    def _create_move_towards(self):
        @tool
        def move_towards(input_json: str) -> str:
            """Move a drone a specific distance in a direction.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)
            - distance: Distance to move in meters (required)
            - heading: Heading direction in degrees 0-360 (optional, default: current heading)
            - dz: Vertical component in meters (optional)

            Example: {{"drone_id": "drone-001", "distance": 10.0, "heading": 90.0}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                distance = params.get('distance')
                heading = params.get('heading')
                dz = params.get('dz')

                if not drone_id:
                    return "Error: drone_id is required"
                if distance is None:
                    return "Error: distance is required"

                result = self.client.move_towards(drone_id, distance, heading, dz)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\", \"distance\": 10.0}}"
            except Exception as e:
                return f"Error moving towards: {str(e)}"
        return move_towards

    def _create_change_altitude(self):
        @tool
        def change_altitude(input_json: str) -> str:
            """Change a drone's altitude while maintaining X/Y position.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)
            - altitude: Target altitude in meters (required)

            Example: {{"drone_id": "drone-001", "altitude": 20.0}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                altitude = params.get('altitude')

                if not drone_id:
                    return "Error: drone_id is required"
                if altitude is None:
                    return "Error: altitude is required"

                result = self.client.change_altitude(drone_id, altitude)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\", \"altitude\": 20.0}}"
            except Exception as e:
                return f"Error changing altitude: {str(e)}"
        return change_altitude

    def _create_hover(self):
        @tool
        def hover(input_json: str) -> str:
            """Command a drone to hover at its current position.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)
            - duration: Optional duration in seconds to hover (optional)

            Example: {{"drone_id": "drone-001", "duration": 5.0}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                duration = params.get('duration')

                if not drone_id:
                    return "Error: drone_id is required"

                result = self.client.hover(drone_id, duration)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\"}}"
            except Exception as e:
                return f"Error hovering: {str(e)}"
        return hover

    def _create_rotate(self):
        @tool
        def rotate(input_json: str) -> str:
            """Rotate a drone to face a specific direction.
            0=North, 90=East, 180=South, 270=West.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)
            - heading: Target heading in degrees 0-360 (required)

            Example: {{"drone_id": "drone-001", "heading": 90.0}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                heading = params.get('heading')

                if not drone_id:
                    return "Error: drone_id is required"
                if heading is None:
                    return "Error: heading is required"

                result = self.client.rotate(drone_id, heading)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\", \"heading\": 90.0}}"
            except Exception as e:
                return f"Error rotating: {str(e)}"
        return rotate

    def _create_return_home(self):
        @tool
        def return_home(input_json: str) -> str:
            """Command a drone to return to its home position.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)

            Example: {{"drone_id": "drone-001"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')

                if not drone_id:
                    return "Error: drone_id is required"

                result = self.client.return_home(drone_id)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\"}}"
            except Exception as e:
                return f"Error returning home: {str(e)}"
        return return_home

    def _create_set_home(self):
        @tool
        def set_home(input_json: str) -> str:
            """Set the drone's current position as its new home position.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)

            Example: {{"drone_id": "drone-001"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')

                if not drone_id:
                    return "Error: drone_id is required"

                result = self.client.set_home(drone_id)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\"}}"
            except Exception as e:
                return f"Error setting home: {str(e)}"
        return set_home

    def _create_calibrate(self):
        @tool
        def calibrate(input_json: str) -> str:
            """Calibrate the drone's sensors.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)

            Example: {{"drone_id": "drone-001"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')

                if not drone_id:
                    return "Error: drone_id is required"

                result = self.client.calibrate(drone_id)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\"}}"
            except Exception as e:
                return f"Error calibrating: {str(e)}"
        return calibrate

    def _create_take_photo(self):
        @tool
        def take_photo(input_json: str) -> str:
            """Command a drone to take a photo.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)

            Example: {{"drone_id": "drone-001"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')

                if not drone_id:
                    return "Error: drone_id is required"

                result = self.client.take_photo(drone_id)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\"}}"
            except Exception as e:
                return f"Error taking photo: {str(e)}"
        return take_photo

    def _create_charge(self):
        @tool
        def charge(input_json: str) -> str:
            """Command a drone to charge its battery.
            Drone must be landed at a charging station.

            Input should be a JSON string with:
            - drone_id: The ID of the drone (required)
            - charge_amount: Amount to charge in percent (required)

            Example: {{"drone_id": "drone-001", "charge_amount": 25.0}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                charge_amount = params.get('charge_amount')

                if not drone_id:
                    return "Error: drone_id is required"
                if charge_amount is None:
                    return "Error: charge_amount is required"

                result = self.client.charge(drone_id, charge_amount)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\", \"charge_amount\": 25.0}}"
            except Exception as e:
                return f"Error charging: {str(e)}"
        return charge

    def _create_send_message(self):
        @tool
        def send_message(input_json: str) -> str:
            """Send a message from one drone to another.

            Input should be a JSON string with:
            - drone_id: The ID of the sender drone (required)
            - target_drone_id: The ID of the recipient drone (required)
            - message: The message content (required)

            Example: {{"drone_id": "drone-001", "target_drone_id": "drone-002", "message": "Hello"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                target_drone_id = params.get('target_drone_id')
                message = params.get('message')

                if not drone_id:
                    return "Error: drone_id is required"
                if not target_drone_id:
                    return "Error: target_drone_id is required"
                if not message:
                    return "Error: message is required"

                result = self.client.send_message(drone_id, target_drone_id, message)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\", \"target_drone_id\": \"drone-002\", \"message\": \"...\"}}"
            except Exception as e:
                return f"Error sending message: {str(e)}"
        return send_message

    def _create_broadcast(self):
        @tool
        def broadcast(input_json: str) -> str:
            """Broadcast a message from one drone to all other drones.

            Input should be a JSON string with:
            - drone_id: The ID of the sender drone (required)
            - message: The message content (required)

            Example: {{"drone_id": "drone-001", "message": "Alert"}}
            """
            try:
                params = json.loads(input_json) if isinstance(input_json, str) else input_json
                drone_id = params.get('drone_id')
                message = params.get('message')

                if not drone_id:
                    return "Error: drone_id is required"
                if not message:
                    return "Error: message is required"

                result = self.client.broadcast(drone_id, message)
                return json.dumps(result, indent=2)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON input: {str(e)}. Expected format: {{\"drone_id\": \"drone-001\", \"message\": \"...\"}}"
            except Exception as e:
                return f"Error broadcasting: {str(e)}"
        return broadcast


def create_uav_tools(client: UAVAPIClient) -> list:
    """
    Create all UAV control tools for LangChain agent

    This is a convenience function that creates a tool registry
    and returns all tools as a list.

    Args:
        client: UAV API client instance

    Returns:
        List of LangChain tools
    """
    registry = UAVToolsRegistry(client)
    return registry.get_all_tools()
