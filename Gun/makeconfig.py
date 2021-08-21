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


CERT_MAKER = """
mkdir -p {dir}/root

openssl genrsa -out {dir}/root/CA.key 2048

openssl req -x509 -new -nodes -key {dir}/root/CA.key -sha256 -days 3650 -out {dir}/root/CA.pem -config {dir}/config/domain.conf

mkdir -p {dir}/domain

openssl req -newkey rsa:2048 -sha256 -nodes -keyout {dir}/domain/domain.key -out {dir}/domain/domain.csr -config {dir}/config/domain.conf

openssl x509 -req -in {dir}/domain/domain.csr -CA {dir}/root/CA.pem -CAkey {dir}/root/CA.key -CAcreateserial -out {dir}/domain/domain.crt -days 397 -sha256 -extfile {dir}/config/domain.ext
"""


SERVER_DIR = input("Input server directory: ").strip().rstrip('/\\')
if not SERVER_DIR:
    raise ValueError("Directory value is empty!")

if SERVER_DIR == '.':
    SERVER_DIR = os.path.abspath('.')

if not os.path.exists(SERVER_DIR):
    raise ValueError("Directory does not exist!")


HOST = input("Input server host: ").strip().strip('/')
if not HOST:
    raise ValueError("Host value is empty!")


COUNTRY_CODE = input("Input 2-chars server Country CODE: ").strip()
if len(COUNTRY_CODE) != 2:
    raise ValueError("Country code is incorrect!")


def make_service():
    folder = os.path.join(SERVER_DIR, "Gun", "service")
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, "passmeta-server-app.service"), 'wb') as file:
        file.write(SERVICE_TEMPLATE.format(server_dir=SERVER_DIR).encode("UTF-8"))


def make_gunicorn_configs():
    folder = os.path.join(SERVER_DIR, "Gun", "service", "config")
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, "autoload.py"), 'wb') as file:
        file.write(CONFIG_TEMPLATE.format(server_dir=SERVER_DIR, daemon=False).encode("UTF-8"))

    with open(os.path.join(folder, "manual.py"), 'wb') as file:
        file.write(CONFIG_TEMPLATE.format(server_dir=SERVER_DIR, daemon=True).encode("UTF-8"))


def make_openssl_configs():
    folder = os.path.join(SERVER_DIR, "Gun", "ssl", "config")
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, "domain.conf"), 'wb') as file:
        file.write(OPENSSL_CONFIG.format(host=HOST, country_code=COUNTRY_CODE).encode("UTF-8"))

    with open(os.path.join(folder, "domain.ext"), 'wb') as file:
        file.write(OPENSSL_EXT.format(host=HOST).encode("UTF-8"))


def make_certmaker():
    with open(os.path.join(SERVER_DIR, "Gun", "ssl", "certmaker.sh"), 'wb') as file:
        file.write(CERT_MAKER.format(dir='/'.join((SERVER_DIR, "Gun", "ssl"))).encode("UTF-8"))


print("Service...")
make_service()

print("Gunicorn configs...")
make_gunicorn_configs()

print("Openssl configs...")
make_openssl_configs()

print("Certmaker...")
make_certmaker()

print("Ready!")
