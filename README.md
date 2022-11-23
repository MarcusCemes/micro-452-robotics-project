# Thymio Robotics Project

_A course project for MICRO-452 as part of MA-RO1 at EPFL, December 2022._

## Prerequisites

In order to run the project, you wil need:

- A Thymio robot
- A camera
- Python 3.10 or higher

Optionally, to use the real-time visualisation tool, you will also need a
modern version of Node.js (>=16).

### Creating a virtual environment

It's recommended to create a "venv" to isolate the Python runtime and dependencies
from your system's global installation for more reliable results.

```powershell
$ python -m venv venv
```

To activate the virtual environment, run the script corresponding to your terminal
(such as `.ps1` for PowerShell):

```powershell
$ .\venv\scripts\Activate.ps1
```

This can be deactivated by simply running:

```powershell
$ deactivate
```

### Installing dependencies

While the virtual environment is activated, run the following command to install
all the required dependencies:

```powershell
$ pip install -r requirements.txt
```

### Setting up the visualisation tool

The visualisation tool is a Node.js application that can be used to display the
robot's camera feed. detected objects and a map with path-finding information
in real-time. For best results, it is recommended to build the application
prior to running it.

```powershell
$ cd ui
$ npm install
$ npm run build
```

## Usage

The application can be run by executing the package as a module:

```powershell
$ python -m app
```

This will attempt to connect to the Thymio driver, lock a Thymio node and
start the main event loop.

To exit the application, press `Ctrl+C` in the terminal.

### Starting the visualisation tool

In a separate terminal, run the following command to start the visualisation:

```powershell
$ cd ui
$ npm run preview
```

This will start a local web server on port `4173`. You can then open the
application in your browser by navigating to
[http://localhost:4173](http://localhost:4173).

## Authors

- Marcus Cemes
- Pablo Palle
- Adrien Pannatier
- Carolina Rodrigues Fidalgo

## License

This project is released under the MIT license.

See [LICENSE](LICENSE).
