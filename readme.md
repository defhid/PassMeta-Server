# PassMeta Server — *your passwords SAFE*
#### © 2024 Vladislav Mironov


### About the project
PassMeta Server is a part of PassMeta System, which provides reliable distributed password management tools.

**Desktop** application is [here](https://github.com/defhid/PassMeta-DesktopApp). <br>
**Web** application is [here](https://github.com/defhid/PassMeta-WebApp).


### Technologies
*Python 3.11, FastAPI, asyncpg + passql, PostgreSQL, Docker.*


### Deployment on Linux

+ **Install [Docker](https://docs.docker.com/engine/install/ubuntu)**
+ **Install utils:**
  - `sudo apt-get update`
  - `sudo apt install unzip nano`
+ **Download and unzip:**
  - `wget https://github.com/defhid/PassMeta-Server/archive/refs/heads/master.zip`
  - `unzip master.zip`
  - `rm master.zip`
  - `mv PassMeta-Server-master /home/passmeta`
+ **Configure:**
  - `nano /home/passmeta/Deploy/.env.local`, enter `APP_ID` + `APP_SECRET_KEY`
  - `cp /home/passmeta/Deploy/scripts/update.sh /home/passmeta-update.sh`
+ **Initialize:** `sudo bash /home/passmeta/Deploy/scripts/configure.sh`
+ **Start:** `sudo bash /home/passmeta/Deploy/scripts/start.sh`
+ **Stop:** `sudo bash /home/passmeta/Deploy/scripts/stop.sh`
+ **Update:** `sudo bash /home/passmeta-update.sh`

### API
Go to `/docs` to see the Swagger API documentation.