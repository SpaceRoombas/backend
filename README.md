# Spaceroombas Game Server

This repo contains the game server for Spaceroombas written in Python. This houses all game state logic, the Spaceroombas interpreter and multiplayer netcode.

# Setup

### Clone
```
git clone https://github.com/SpaceRoombas/backend.git spaceroombas-server
cd spaceroombas-server
```

### (OPTIONAL, BUT RECOMMENDED) Setup virtual environment

```
python -m venv venv
```

> Powershell (Windows)

```
.\venv\Scripts\Activate.ps1
```

> Everyone else

```
source venv/bin/activate
```

### Install deps

```
pip install -r requirements.txt
```

## Running standalone game session server

This method is primarily intended for testing. This will run a server for game sessions on a default port of `9001`.

```
python spaceroombas/session_server.py
```

### Verbose output

Set the `LOGLEVEL` environment variable to `INFO` or `DEBUG` for additional logging output:

```
LOGLEVEL=DEBUG python spaceroombas/session_server.py
```

# Setup with Docker

Build image

```
docker build -t roombots-server .
```

Run image:

```
docker run --network host -p 9000-9100:9000-9100 -d roombots-server
```