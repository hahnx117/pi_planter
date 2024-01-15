FROM python:3.11-slim-bookworm

RUN apt update && apt install python3-dev gcc -y

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]

