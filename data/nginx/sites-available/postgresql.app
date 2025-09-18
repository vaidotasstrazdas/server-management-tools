server {
    listen 80;
    server_name postgresql.{{DOMAIN_NAME}};
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name postgresql.{{DOMAIN_NAME}};

    ssl_certificate     /etc/ssl/certs/internal.crt;
    ssl_certificate_key /etc/ssl/private/internal.key;

    allow 10.10.0.2;   # admin
    deny  all;

    location / {
        proxy_pass                          http://127.0.0.1:8081;
        proxy_set_header Host               $host;
        proxy_set_header X-Real-IP          $remote_addr;
        proxy_set_header X-Forwarded-For    $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto  $scheme;
    }
}
