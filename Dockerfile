FROM python:3.9-slim-buster
LABEL authors="aleksey_kiryukhin"

WORKDIR /server
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_APP=server.py
CMD ["flask", "run", "--host", "0.0.0.0"]