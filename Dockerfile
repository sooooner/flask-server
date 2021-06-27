FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./app /app
RUN apt-get update 
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get -y install libgl1-mesa-glx
