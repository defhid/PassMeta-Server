# PassMeta Server — *your passwords SAFE*
#### © 2025 Vladislav Mironov


## About the project
PassMeta Server is a part of PassMeta System, which provides reliable distributed password management tools.

**Desktop** application is [here](https://github.com/defhid/PassMeta-DesktopApp). <br>
**Web** application is [here](https://github.com/defhid/PassMeta-WebApp).

### Technologies
*Python 3.11, FastAPI, asyncpg + passql, PostgreSQL, Docker.*


## Deployment on Linux

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
  - `nano /home/passmeta/Deploy/.env.local`, enter `APP_ID` (see [application id](#Application-ID)), `APP_SECRET_KEY` (see [secret key](#Fernet-secret-key)), `UVICORN_CORS_PATTERN` (see [cors](#CORS-policy)).
  - `cp /home/passmeta/Deploy/scripts/update.sh /home/passmeta-update.sh`
  - `sudo bash /home/passmeta/Deploy/scripts/configure.sh`
+ **Configure existing SSL:**
  - `docker cp -L {your_path_to}/fullchain.pem passmeta-configurator:/etc/passmeta/ssl/cert.pem`
  - `docker cp -L {your_path_to}/privkey.pem passmeta-configurator:/etc/passmeta/ssl/key.pem`
+ **Build:** `sudo bash /home/passmeta/Deploy/scripts/rebuild.sh`
+ **Start:** `sudo bash /home/passmeta/Deploy/scripts/start.sh`
+ **Stop:** `sudo bash /home/passmeta/Deploy/scripts/stop.sh`
+ **Update:** `sudo bash /home/passmeta-update.sh`

## API
Go to `/docs` to see Swagger API documentation.

## Help

### Application ID

To differentiate between server applications, each app has its own unique identifier. If you're creating a new application, the best way is to generate new uuid string, python shell:
```python
from uuid import uuid4
print(uuid4())
```

### Fernet secret key

The server has an additional layer of security in the form of symmetric encryption. The algorithm requires a secret key to be generated using Fernet, python shell:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key())
```

**Important:** You should create a backup of your secret key, because if you reinstall the application and forget the key, you lose all your remote files.

### CORS policy

The most web browsers have a built-in security policy that declines cross-origin requests that are not explicitly allowed.
So you should specify a regex pattern that includes all the hostnames hosting your web applications.

That is **not required** if you are not using the web application, or you have a proxy for development.
You can also specify `*` to allow any hostname, but this is **not recommended**.
