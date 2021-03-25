FROM python:3.8-slim

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends git

COPY . /discordbot

RUN pip install -r /discordbot/requirements.txt

ENV DISCORD_TOKEN discord_token
ENV TWITCH_ID twitch_id
ENV TWITCH_SECRET twitch_secret
ENV REDIS_HOST redis_host
ENV REDIS_PORT redis_port
ENV REDIS_PASSWORD redis_password

ENTRYPOINT ["python", "/discordbot/discord_bot.py"]
