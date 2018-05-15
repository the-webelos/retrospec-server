FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./retro /app/retro
COPY ./uwsgi.ini /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
