FROM python:3.8-alpine
WORKDIR /api
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev bash
RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install --system
COPY . /api
RUN find . -name "*.pyc" -exec rm -f {} \;
ENTRYPOINT /bin/bash -c "flask run"
