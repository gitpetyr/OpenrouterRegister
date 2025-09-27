FROM python:3.11-slim
RUN apt update && \
    apt install -y wget xvfb gnupg

RUN apt install software-properties-common apt-transport-https ca-certificates curl -y

RUN mkdir -p /etc/apt/keyrings && \
    wget -q -O /etc/apt/keyrings/google-chrome.gpg https://dl.google.com/linux/linux_signing_key.pub && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install DrissionPage PyVirtualDisplay

CMD ["python3", "main_docker.py"]
