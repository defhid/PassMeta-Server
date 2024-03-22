import subprocess

def generate_ssl_certificate(
    output_path: str,
    common_name: str,
    country_code: str,
    organization: str,
    state: str,
    locality: str
):
    if len(country_code) != 2:
        raise ValueError("Country code is incorrect!")

    subject_dict = {
        'C': country_code,
        'ST': state,
        'L': locality,
        'O': organization,
        'CN': common_name,
    }
    subject_line = "".join(map(lambda x: f"/{x[0]}={x[1]}", subject_dict.items()))

    subprocess.run(
        f"openssl req -x509 -newkey rsa:4096 -keyout {output_path}/key.pem -out {output_path}/cert.pem -sha256 -days 3650 -nodes -subj \"{subject_line}\"",
        shell=True
    )
