# Gunicorn setup
- `pip install gunicorn` (in venv, already in requirements.txt)
- Create a systemd config file:
- `sudo nano /etc/systemd/system/lp-webservice.service`
    ```
    [Unit]
    Description=Gunicorn instance to serve live papers
    After=network.target
    
    [Service]
    User=ubuntu
    WorkingDirectory=/home/ubuntu/github/LP-WebService
    ExecStart=/home/ubuntu/github/LP-WebService/.venv/bin/gunicorn -b localhost:5000 -w 4 app:app
    Restart=always
    
    [Install]
    WantedBy=multi-user.target
    ```
- `sudo systemctl daemon-reload`
- `sudo systemctl start lp-webservice`