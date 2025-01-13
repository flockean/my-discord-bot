FROM python:3.12-slim
COPY requirements.txt ./

ARG DISCORD_BOT
ENV DISCORD_BOT=$DISCORD_BOT

RUN pip install -U pip
RUN pip install -r requirements.txt

WORKDIR /app
COPY main.py ./
COPY ./src ./src


ENTRYPOINT ["python3", "main.py"]
