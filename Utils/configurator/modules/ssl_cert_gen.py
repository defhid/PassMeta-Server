import subprocess

def generate_ssl_certificate(output_path: str, country_code: str, host: str):
    subject_dict = {
        'C': country_code,
        'ST': "State",
        'L': "City",
        'O': "Company",
        'CN': host,
    }
    subject_line = "".join(map(lambda x: f"/{x[0]}={x[1]}", subject_dict.items()))

    subprocess.run(
        f"openssl req -x509 -newkey rsa:4096 -keyout {output_path}/key.pem -out {output_path}/cert.pem -sha256 -days 3650 -nodes -subj \"{subject_line}\"",
        shell=True
    )
