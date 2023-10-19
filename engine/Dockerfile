FROM python:3.9-slim

WORKDIR /usr/src/app

COPY . .

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc  -y

RUN pip install pipenv --no-cache-dir && \
    pipenv install --system --deploy --ignore-pipfile && \
    pip uninstall -y pipenv virtualenv-clone virtualenv

EXPOSE 15002

CMD [ "python", "app.py" ]