# syntax=docker/dockerfile:1
FROM python:3.8


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "ticker.py"]