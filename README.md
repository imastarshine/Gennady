# Gennady

Gennady is a Telegram bot that remembers messages from chat and sends them whenever a message is received
Gennady can remember any media and learns Markov chain

## Let's set this up on your system

1. Clone repository to your machine
```bash
git clone https://github.com/imastarshine/Gennady.git
cd Gennady
```

2. Install dependencies (requires: Python >= 3.12 & Poetry 2)

```bash
poetry config virtualenvs.in-project true
poetry install 
```

3. Set up `.env` file
```dotenv
TELEGRAM_BOT_TOKEN=""  # Take telegram bot token from @BotFather
TELEGRAM_CHAT_TO_LISTEN=""  # Your chat ID
TELEGRAM_BOT_SOCKS5_PROXY=""  # Socks5 Proxy in format socks5://login:password@ip:port OR socks5://ip:port
```

4. Now we can start it
```bash
poetry run python3 main.py 
```

5. Or you can set it up as a systemd service
```ini
[Unit]
Description=Gennady
After=network.target
[Service]
User=<ANY>
UMask=0002
WorkingDirectory=<YOUR_DIR>
ExecStart=<YOUR_DIR>/.venv/bin/python <YOUR_DIR>/main.py
Restart=always
RestartSec=240
Environment=PYTHONUNBUFFERED=1
[Install]
WantedBy=multi-user.target 
```

## Docker

Build docker image (linux/amd64)
```bash
docker build --platform linux/amd64 -t gennady:latest .
docker save gennady:latest | gzip > gennady.tar.gz
```

On your server machine (move gennady.tar.gz to directory)
```bash
cd /opt/app
docker load -i gennady.tar.gz

docker images
```

Start docker image
```bash
docker run -d \
  --name gennady \
  --restart unless-stopped \
  -v $(pwd)/.env:/app/.env \
  gennady:latest
```
