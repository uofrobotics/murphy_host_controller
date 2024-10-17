# murphy_host_controller

(Utility Robot) Code for the host computer that takes in controller input and sends it over UDP to the Jetson Nano. 

### Features

1. Read controller input from a host computer using Pygame.
2. Send controller input data over UDP to a specified IP address and port.

### Installation

- Clone the repository:

``` bash
git clone https://github.com/uofrobotics/Host2Jetson.git
```
- Setup virtual environment

``` bash
python -m venv venv
```

- Start virtual environment

- Install the required dependencies:
``` bash
pip install -r requirements.txt
```

- Create .env file with `JETSON_IP` and `JETSON_PORT`

### Usage

1. Connect your controller input device (needs atleast 2 axes) to the host computer.


2. Run `udp_send.py`

``` bash
python3 udp_send.py
```