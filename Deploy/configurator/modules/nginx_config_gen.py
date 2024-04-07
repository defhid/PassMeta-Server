def generate_nginx_configuration(output_path: str, api_only: bool):
    ui_location = """
        location / {
            resolver 127.0.0.11 ipv6=off;
            proxy_pass http://passmeta-ui-server:8000;
            proxy_connect_timeout 5;
        }
    """ if not api_only else ""

    web_location = """
        location /api/ {
            resolver 127.0.0.11 ipv6=off;
            rewrite ^/api/(.*) /$1 break;
            proxy_pass http://passmeta-web-server:8000$uri$is_args$args;
            proxy_connect_timeout 10;
        }
    """

    with open(f"{output_path}/default.conf", "w") as f:
        f.write(f"""
            server {{
                listen 80;
                listen [::]:80;
                http2 on;
            
                return 301 https://$host$request_uri;

                access_log /var/log/nginx/server-access.log;
                error_log /var/log/nginx/server-error.log warn;
            }}
            
            server {{
                listen 443 default_server ssl;
                listen [::]:443 ssl;
                http2 on;
            
                ssl_certificate /etc/nginx/ssl/cert.pem;
                ssl_certificate_key /etc/nginx/ssl/key.pem;
            
                {ui_location}
                {web_location}

                access_log /var/log/nginx/server-access.log;
                error_log /var/log/nginx/server-error.log warn;
            }}
        """)
