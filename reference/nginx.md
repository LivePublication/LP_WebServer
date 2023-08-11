# NGINX setup steps
(note that this was written from memory, may be incomplete)
Files edited:
- /etc/nginx/nginx.conf
  - Added `include /etc/nginx/sites-enabled/*;` to the end of the `http` block in nginx.conf
- /etc/nginx/sites-available/default
  - Added `server_name _;` to the `server` block in default
  - Added `location` block to the `server` block in default:
    ```
    location / {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Fowarded-Proto $scheme;
        proxy_set_header X-Fowarded-Host $host;
        proxy_set_header X-Fowarded-Prefix $prefix /;
    }
    ```
