FROM python:3.9

WORKDIR /usr/app/src

COPY .. ./

RUN pip install --upgrade pip
RUN pip install -r ./deploy/requirements.txt

CMD ["python", "main.py"]