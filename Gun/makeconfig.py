import os

# Creates:
#   Gun/service/passmeta-server-app.service
#
#   Gun/config/autoload.py
#   Gun/config/manual.py
#
#   Gun/ssl/config/domain.conf
#   Gun/ssl/config/domain.ext


SERVICE_TEMPLATE = """
[Unit]
Description=EntrantServerApplication
[Service]
Type=simple
ExecStart={server_dir}/env/bin/python -m gunicorn --config {server_dir}/Gun/service/config/autoload.py
[Install]
WantedBy=multi-user.target
""".strip()


CONFIG_TEMPLATE = """
chdir = r'{server_dir}'
wsgi_app = 'main:app'
bind = ['0.0.0.0:8080']
worker_class = 'uvicorn.workers.UvicornWorker'
workers = 1
daemon = {daemon}
pidfile = 'Gun/service/process.pid'
keyfile = 'Gun/ssl/domain/domain.key'
certfile = 'Gun/ssl/domain/domain.crt'
accesslog = 'Gun/access_logs.txt'
access_log_format = '%(h)s %(t)s "%(r)s" %(s)s'
errorlog = 'Gun/logs.txt'
loglevel = 'info'
""".strip()


OPENSSL_CONFIG = """
[ req ]
distinguished_name          = req_distinguished_name
prompt                      = no

[ req_distinguished_name ]
countryName                 = {country_code}
stateOrProvinceName         = None
localityName                = None
0.organizationName          = Passmeta Ltd
organizationalUnitName      = Communication Department
commonName                  = {host}
emailAddress                = None
""".strip()


OPENSSL_EXT = """
authorityKeyIdentifier  = keyid,issuer
basicConstraints        = CA:FALSE
keyUsage                = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName          = @alt_names

[alt_names]
DNS.1       = %%{host}%%
""".strip()


SERVER_DIRECTORY = input("Input server directory: ").strip().rstrip('/\\')
if not SERVER_DIRECTORY:
    raise ValueError("Directory value is empty!")

if SERVER_DIRECTORY == '.' or not SERVER_DIRECTORY:
    SERVER_DIRECTORY = os.path.abspath('.')

if not os.path.exists(SERVER_DIRECTORY):
    raise ValueError("Directory does not exist!")


HOST = input("Input server host: ").strip().strip('/')
if not HOST:
    raise ValueError("Host value is empty!")


COUNTRY_CODE = input("Input 2-chars server Country CODE: ").strip()
if len(COUNTRY_CODE) != 2:
    raise ValueError("Country code is incorrect!")


def make_service():
    folder = os.path.join(SERVER_DIRECTORY, "Gun", "service")
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, "passmeta-server-app.service"), 'wb') as file:
        file.write(SERVICE_TEMPLATE.format(server_dir=SERVER_DIRECTORY).encode("UTF-8"))


def make_gunicorn_configs():
    folder = os.path.join(SERVER_DIRECTORY, "Gun", "service", "config")
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, "autoload.py"), 'wb') as file:
        file.write(CONFIG_TEMPLATE.format(server_dir=SERVER_DIRECTORY, daemon=False).encode("UTF-8"))

    with open(os.path.join(folder, "manual.py"), 'wb') as file:
        file.write(CONFIG_TEMPLATE.format(server_dir=SERVER_DIRECTORY, daemon=True).encode("UTF-8"))


def make_openssl_configs():
    folder = os.path.join(SERVER_DIRECTORY, "Gun", "ssl", "config")
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, "domain.conf"), 'wb') as file:
        file.write(OPENSSL_CONFIG.format(host=HOST, country_code=COUNTRY_CODE).encode("UTF-8"))

    with open(os.path.join(folder, "domain.ext"), 'wb') as file:
        file.write(OPENSSL_EXT.format(host=HOST).encode("UTF-8"))


print("Service file...")
make_service()

print("Gunicorn config files...")
make_gunicorn_configs()

print("Openssl config files...")
make_openssl_configs()

print("Ready!")
