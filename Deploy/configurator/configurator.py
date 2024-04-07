from modules.nginx_config_gen import generate_nginx_configuration
from modules.ssl_cert_gen import generate_ssl_certificate
import os


def get_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise ValueError(f"{name} is empty!")


if input("Generate SSL certificate? (y/n) ").lower() == "y":
    generate_ssl_certificate(
        output_path=f"/etc/passmeta/ssl",
        common_name=get_env("CERT_COMMON_NAME"),
        country_code=get_env("CERT_COUNTRY_CODE"),
        organization=get_env("CERT_ORGANIZATION"),
        state=get_env("CERT_STATE"),
        locality=get_env("CERT_LOCALITY"),
    )

mode = input("Select mode (api-only/full/pass) ").lower()

if mode == "api-only" or mode == "full":
    generate_nginx_configuration(
        output_path=f"/etc/passmeta/nginx",
        api_only=(mode == "api-only"),
    )

print("Ready!")
