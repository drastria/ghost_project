Ghost Project is a simple yet effective Python tool that combines a high-speed, multi-threaded port scanner with a simulated UDP flood attack module. It's designed to quickly find open ports on a target and then, upon user confirmation, launch a basic stress test.

## Legal disclaimer :
Usage of Ghost Project for attacking targets without prior mutual consent is illegal. It's the end user's responsibility to obey all applicable local, state and federal laws. The author assumes no liability and is not responsible for any misuse or damage caused by this program.

### Picture
![Ghost](https://github.com/user-attachments/assets/7ec91817-86ce-4107-bd22-ad33a86bd85d)

### Features
- Fast Multi-threaded Scanning: Utilizes ThreadPoolExecutor to scan ports concurrently, significantly speeding up discovery
- Smart Port Prioritization: Checks a list of common ports first to find potential openings faster
- Automatic Discovery: Scans and stops as soon as the desired number of open ports is found
- Simulated Attack Module: Includes a function to initiate a UDP flood on a discovered open port
- Clean UI: Features a unique ASCII art banner and clear, real-time progress updates
- No Dependencies: Runs using only standard Python libraries

### Requirements
- Python 3.x

### Usage:
```
git clone https://github.com/drastria/ghost_project
cd ghost_project
python ghost.py
```

### How it works?

The script operates in two main phases. First, the scanning phase, where it resolves the provided hostname to an IP address and launches hundreds of threads to check for open TCP ports. It prioritizes common ports like 80, 443, and 22 before moving through all 65,535 possible ports.

Once an open port is identified, the tool enters the attack phase. If the user confirms, it initiates a simple but continuous UDP packet flood to the target's IP on the specified port, effectively stress-testing the connection.

### Donate!
Support the authors:

[![Donate using Trakteer](https://new.trakteer.id/_assets/v11/f005987b6b7970f1696c6a8e2306d192f63a03ae.png)](https://trakteer.id/drastria/gift)
