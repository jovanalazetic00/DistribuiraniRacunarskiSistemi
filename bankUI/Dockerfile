FROM python:3.9.13-alpine

WORKDIR /usr/src/app

COPY . .

RUN pip3 install pipenv --no-cache-dir && \
    pipenv install --system --deploy --ignore-pipfile && \
    pip3 uninstall -y pipenv virtualenv-clone virtualenv

EXPOSE 15001

CMD [ "python", "main.py" ]
