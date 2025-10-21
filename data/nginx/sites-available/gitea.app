server {
    listen 80;
    server_name gitea.{{DOMAIN_NAME}};
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name gitea.{{DOMAIN_NAME}};

    ssl_certificate     /etc/ssl/certs/internal.crt;
    ssl_certificate_key /etc/ssl/private/internal.key;

    # Allow only VPN clients (further restrict if desired)
    allow 10.10.0.0/24;
    deny  all;

    client_max_body_size 512m;

    location / {
        proxy_http_version                  1.1;
        proxy_set_header Host               $host;
        proxy_set_header X-Forwarded-Host   $host;
        proxy_set_header X-Real-IP          $remote_addr;
        proxy_set_header X-Forwarded-For    $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto  $scheme;
        proxy_read_timeout                  3600;
        proxy_pass                          http://127.0.0.1:3000;
    }

}
