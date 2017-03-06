# Atmosphere Station

|Branch|Travis|
|------|:------:|
|master|[![Build Status](https://img.shields.io/travis/atmospherehub/atmosphere-station/master.svg)](https://travis-ci.org/atmospherehub/atmosphere-station.svg?branch=master)|


The app runs on RPi and detects faces using Haar cascade classifier from video stream. 
Once the face detected it sends the image via HTTP to the configurable endpoint.

## Running application

Make sure that all required packages installed from `apt-requirments.txt` and `requirments.txt` files. And then simply execute:

```
python . -e https://posttestserver.com/post.php
```

> On Raspberry Pi you will have to compile OpenCV from source.

## Running as daemon service

Add environment variable to configure endpoint to `/etc/environment`:
```
ATMOSPHERE_ENDPOINT=http://...
```

Then execute `sudo visudo` and add:
```
Defaults    env_keep +="ATMOSPHERE_ENDPOINT"
```

Assuming that the project cloned into `/home/pi/atmosphere-station` (this can me changed in `atmosphere-station.sh`), copy init script to `/etc/init.d`:

```bash
sudo cp atmosphere-station.sh /etc/init.d
```

Make sure that both `atmosphere-station.sh` and `__main__.py` are executable:

```bash
sudo chmod 755 /etc/init.d/atmosphere-station.sh
chmod 755 __main__.py
```

At this stage you can start and stop service:
```bash
sudo /etc/init.d/atmosphere-station.sh start
sudo /etc/init.d/atmosphere-station.sh status
sudo /etc/init.d/atmosphere-station.sh stop
```
> Note that when service started it will perform `git pull` to update the app. See details in `atmosphere-station.sh` file

See log file at `/tmp/atmosphere-station.log` for info or errors.

Now, add it to the boot sequence:
```bash
sudo update-rc.d atmosphere-station.sh defaults
```
