"""
Generates
"""
from modules.nginx_config_gen import generate_nginx_configuration
from modules.ssl_cert_gen import generate_ssl_certificate
import os


def get_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise ValueError(f"{name} is empty!")


external_host = get_env("PASSMETA_EXTERNAL_HOST")
internal_host = get_env("PASSMETA_INTERNAL_HOST")
internal_port = int(get_env("PASSMETA_INTERNAL_PORT"))

country_code = get_env("PASSMETA_COUNTRY_CODE")
if len(country_code) != 2:
    raise ValueError("Country code is incorrect!")

generate_ssl_certificate(
    output_path=f"/etc/passmeta/ssl",
    country_code=country_code,
    host=external_host)

generate_nginx_configuration(
    output_path=f"/etc/passmeta/nginx",
    internal_host=internal_host,
    internal_port=internal_port,
)

print("Ready!")
