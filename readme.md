# PassMeta Server — *your passwords SAFE*
#### © 2024 Vladislav Mironov


### About the project
PassMeta Server is a part of PassMeta System, which provides reliable
<br>
distributed password storage and password management tools.

**Desktop** application is [here](https://github.com/defhid/PassMeta-DesktopApp).


### Technologies
*Python 3.11, FastAPI, asyncpg + passql, PostgreSQL, Docker.*


### Deployment on Linux

+ **Install [Docker](https://docs.docker.com/engine/install/ubuntu)**


+ **Install utils:**
  - `sudo apt-get update`
  - `sudo apt install unzip nano`


+ **Download and unzip the project, change current directory:**
  - `wget https://github.com/defhid/PassMeta-Server/archive/refs/heads/master.zip`
  - `unzip master.zip`
  - `rm master.zip`
  - `mv PassMeta-Server-master /home/passmeta`
  - `cd /home/passmeta`


+ **Configure docker-compose:**
  - TODO ...
  - input username for local PostgreSQL server
  - input password for that user
  - input server host, like `x.x.x.x` or `my-server-host.com`
  - input server country code, like `RU`


### Launch as service

+ **Initialization:**
  - `docker compose create configurator`
  - `docker compose start configurator`
  - `docker compose create`


+ **Start-stop:**
  - `docker compose start`
  - `docker compose stop`


### Update
+ `sudo bash Utils/updater.sh`
