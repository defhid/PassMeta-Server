def generate_nginx_configuration(output_path: str, internal_host: str, internal_port: int):
    with open(f"{output_path}/default.conf", "w") as f:
        f.write(f"""
            server {{
                listen 80;
                listen [::]:80;
                http2 on;

                return 301 https://$host$request_uri;
            }}

            server {{
                listen 443 default_server ssl;
                listen [::]:443 ssl;
                http2 on;

                ssl_certificate /etc/nginx/ssl/cert.pem;
                ssl_certificate_key /etc/nginx/ssl/key.pem;

                error_log /var/log/nginx/error.log warn;

                location /api/ {{
                    proxy_pass http://{internal_host}:{internal_port};
                }}
            }}
        """)
