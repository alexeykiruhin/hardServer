FROM python:3.8-slim-buster
LABEL authors="aleksey_kiryukhin"

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_APP=server.py
CMD ["flask", "run", "--host", "0.0.0.0"]

ENTRYPOINT ["top", "-b"]