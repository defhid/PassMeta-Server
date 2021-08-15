import os

# Creates:
#   Gun/service/passmeta-server-app.service
#   Gun/config/autoload.py
#   Gun/config/manual.py


SERVICE_TEMPLATE = """
[Unit]
Description=EntrantServerApplication
[Service]
Type=simple
ExecStart={server_dir}/env/bin/python -m gunicorn --config {server_dir}/Gun/service/config/autoload.py
[Install]
WantedBy=multi-user.target
"""

CONFIG_TEMPLATE = """
chdir = r'{server_dir}'
wsgi_app = 'main:app'
bind = ['0.0.0.0:8080']
worker_class = 'uvicorn.workers.UvicornWorker'
workers = 1
daemon = {daemon}
pidfile = 'Gun/service/process.pid'
errorlog = 'Gun/logs.txt'
"""

SERVER_DIRECTORY = input("Input server directory: ").strip().rstrip('/\\')
if SERVER_DIRECTORY == '.' or not SERVER_DIRECTORY:
    SERVER_DIRECTORY = os.path.abspath('.')

if not os.path.exists(SERVER_DIRECTORY):
    raise ValueError("Directory does not exist!")


folder = os.path.join(SERVER_DIRECTORY, "Gun", "service")
if not os.path.exists(folder):
    os.makedirs(folder)

with open(os.path.join(folder, "passmeta-server-app.service"), 'wb') as file:
    file.write(SERVICE_TEMPLATE.format(server_dir=SERVER_DIRECTORY).encode("UTF-8"))


folder = os.path.join(SERVER_DIRECTORY, "Gun", "service", "config")
if not os.path.exists(folder):
    os.makedirs(folder)

with open(os.path.join(folder, "autoload.py"), 'wb') as file:
    file.write(CONFIG_TEMPLATE.format(server_dir=SERVER_DIRECTORY, daemon=False).encode("UTF-8"))

with open(os.path.join(folder, "manual.py"), 'wb') as file:
    file.write(CONFIG_TEMPLATE.format(server_dir=SERVER_DIRECTORY, daemon=True).encode("UTF-8"))


print("Created")
