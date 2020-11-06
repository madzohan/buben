FROM python:3.8-alpine
WORKDIR /api
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev
RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install --system --deploy
COPY . /api
RUN find . -name "*.pyc" -exec rm -f {} \;
ENTRYPOINT flask run
