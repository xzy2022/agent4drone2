# UAV Control Tools Reference

This document provides a comprehensive reference of all available UAV (drone) control tools in the system.

**Last Updated:** 2026-01-09

---

## Table of Contents

- [Information Gathering Tools](#information-gathering-tools)
- [Flight Control Tools](#flight-control-tools)
- [Utility Tools](#utility-tools)
- [Communication Tools](#communication-tools)

---

## Information Gathering Tools

### list_drones

List all available drones in the current session with their status, battery level, and position.

**Use Case:** Check what drones are available before trying to control them.

**Parameters:** None

**Example:**
```json
{}
```

**Returns:** JSON array of drones with their current status, battery levels, and positions.

---

### get_session_info

Get current session information including task type, statistics, and status.

**Use Case:** Understand what mission you need to complete.

**Parameters:** None

**Example:**
```json
{}
```

**Returns:** JSON object containing session details, task information, and current status.

---

### get_task_progress

Get mission task progress including completion percentage and status.

**Use Case:** Track mission completion and see how close you are to finishing.

**Parameters:** None

**Example:**
```json
{}
```

**Returns:** JSON object with progress percentage, status message, and completion flag.

---

### get_weather

Get current weather conditions including wind speed, visibility, and weather type.

**Use Case:** Check this before takeoff to ensure safe flying conditions.

**Parameters:** None

**Example:**
```json
{}
```

**Returns:** JSON object with weather conditions (wind speed, visibility, weather type).

---

### get_drone_status

Get detailed status of a specific drone including position, battery, heading, and visited targets.

**Parameters:**
- `drone_id` (string, required): The ID of the drone

**Example:**
```json
{
  "drone_id": "drone-001"
}
```

**Returns:** JSON object with detailed drone status information.

---

### get_nearby_entities

Get drones, targets, and obstacles near a specific drone (within its perception radius).

**Parameters:**
- `drone_id` (string, required): The ID of the drone

**Example:**
```json
{
  "drone_id": "drone-001"
}
```

**Returns:** JSON object listing nearby entities with their positions and types.

---

## Flight Control Tools

### take_off

Command a drone to take off to a specified altitude. Drone must be on ground (idle or ready status).

**Parameters:**
- `drone_id` (string, required): The ID of the drone
- `altitude` (float, optional): Target altitude in meters (default: 10.0)

**Example:**
```json
{
  "drone_id": "drone-001",
  "altitude": 15.0
}
```

**Returns:** JSON object confirming takeoff command with resulting altitude.

---

### land

Command a drone to land at its current position.

**Parameters:**
- `drone_id` (string, required): The ID of the drone

**Example:**
```json
{
  "drone_id": "drone-001"
}
```

**Returns:** JSON object confirming landing command.

---

### move_to

Move a drone to specific 3D coordinates (x, y, z). Always check for collisions first.

**Parameters:**
- `drone_id` (string, required): The ID of the drone
- `x` (float, required): Target X coordinate in meters
- `y` (float, required): Target Y coordinate in meters
- `z` (float, required): Target Z coordinate (altitude) in meters

**Example:**
```json
{
  "drone_id": "drone-001",
  "x": 100.0,
  "y": 50.0,
  "z": 20.0
}
```

**Returns:** JSON object with movement result and new position.

---

### move_towards

Move a drone a specific distance in a direction.

**Parameters:**
- `drone_id` (string, required): The ID of the drone
- `distance` (float, required): Distance to move in meters
- `heading` (float, optional): Heading direction in degrees 0-360 (default: current heading)
- `dz` (float, optional): Vertical component in meters

**Example:**
```json
{
  "drone_id": "drone-001",
  "distance": 10.0,
  "heading": 90.0
}
```

**Returns:** JSON object with movement result and new position.

**Note:** Heading: 0=North, 90=East, 180=South, 270=West

---

### change_altitude

Change a drone's altitude while maintaining X/Y position.

**Parameters:**
- `drone_id` (string, required): The ID of the drone
- `altitude` (float, required): Target altitude in meters

**Example:**
```json
{
  "drone_id": "drone-001",
  "altitude": 20.0
}
```

**Returns:** JSON object confirming altitude change.

---

### hover

Command a drone to hover at its current position.

**Parameters:**
- `drone_id` (string, required): The ID of the drone
- `duration` (float, optional): Duration in seconds to hover

**Example:**
```json
{
  "drone_id": "drone-001",
  "duration": 5.0
}
```

**Returns:** JSON object confirming hover command.

---

### rotate

Rotate a drone to face a specific direction.

**Parameters:**
- `drone_id` (string, required): The ID of the drone
- `heading` (float, required): Target heading in degrees 0-360

**Example:**
```json
{
  "drone_id": "drone-001",
  "heading": 90.0
}
```

**Returns:** JSON object confirming rotation with new heading.

**Note:** 0=North, 90=East, 180=South, 270=West

---

### return_home

Command a drone to return to its home position.

**Parameters:**
- `drone_id` (string, required): The ID of the drone

**Example:**
```json
{
  "drone_id": "drone-001"
}
```

**Returns:** JSON object confirming return home command.

---

## Utility Tools

### set_home

Set the drone's current position as its new home position.

**Parameters:**
- `drone_id` (string, required): The ID of the drone

**Example:**
```json
{
  "drone_id": "drone-001"
}
```

**Returns:** JSON object confirming new home position.

---

### calibrate

Calibrate the drone's sensors.

**Parameters:**
- `drone_id` (string, required): The ID of the drone

**Example:**
```json
{
  "drone_id": "drone-001"
}
```

**Returns:** JSON object confirming calibration command.

---

### take_photo

Command a drone to take a photo.

**Parameters:**
- `drone_id` (string, required): The ID of the drone

**Example:**
```json
{
  "drone_id": "drone-001"
}
```

**Returns:** JSON object with photo capture result and file path.

---

### charge

Command a drone to charge its battery. Drone must be landed at a charging station.

**Parameters:**
- `drone_id` (string, required): The ID of the drone
- `charge_amount` (float, required): Amount to charge in percent

**Example:**
```json
{
  "drone_id": "drone-001",
  "charge_amount": 25.0
}
```

**Returns:** JSON object with charging status and new battery level.

---

## Communication Tools

### send_message

Send a message from one drone to another.

**Parameters:**
- `drone_id` (string, required): The ID of the sender drone
- `target_drone_id` (string, required): The ID of the recipient drone
- `message` (string, required): The message content

**Example:**
```json
{
  "drone_id": "drone-001",
  "target_drone_id": "drone-002",
  "message": "Hello"
}
```

**Returns:** JSON object confirming message delivery.

---

### broadcast

Broadcast a message from one drone to all other drones.

**Parameters:**
- `drone_id` (string, required): The ID of the sender drone
- `message` (string, required): The message content

**Example:**
```json
{
  "drone_id": "drone-001",
  "message": "Alert"
}
```

**Returns:** JSON object confirming broadcast to all drones.

---

## Tool Categories Summary

| Category | Tools Count | Purpose |
|----------|-------------|---------|
| Information Gathering | 6 | Query system state, drone status, weather, and session info |
| Flight Control | 8 | Control drone movement, takeoff, landing, and orientation |
| Utility | 4 | Manage home position, calibration, photos, and battery charging |
| Communication | 2 | Inter-drone messaging and broadcasting |

**Total Tools:** 20

---

## Common Error Messages

All tools may return the following error messages:

- `"Error: drone_id is required"` - Missing required drone_id parameter
- `"Error parsing JSON input: ..."` - Invalid JSON format in input
- `"Error: <parameter> is required"` - Missing other required parameters

---

## Coordinate System

The UAV system uses a 3D Cartesian coordinate system:

- **X-axis:** East-West (positive = East)
- **Y-axis:** North-South (positive = North)
- **Z-axis:** Altitude (positive = Up)

All coordinates are in meters.

---

## Heading Reference

| Degrees | Direction |
|---------|-----------|
| 0° | North |
| 90° | East |
| 180° | South |
| 270° | West |

---

## Usage Notes

1. **Always check drone status** before issuing movement commands
2. **Check weather conditions** before takeoff for safe operations
3. **Use list_drones first** to get valid drone IDs
4. **Check battery levels** regularly to avoid mid-flight failures
5. **Return drones home** after mission completion
6. **Land drones** at charging stations before charging

---

## API Reference

For implementation details, see: `src/tools/uav_tools.py`

For API client methods, see: `src/api_client.py`
