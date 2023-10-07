FROM python:3.10-slim

ENV ENV_TYPE=production \
  TZ=Europe/Helsinki \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.5.1

RUN apt-get update && \
    apt-get install -y tk python3-dev

    
RUN pip install "poetry==$POETRY_VERSION"


WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY poetry.lock pyproject.toml /app/

#RUN poetry config virtualenvs.create false
#RUN poetry install --no-dev --no-interaction --no-ansi --no-root

COPY . /app

ENV API_TOKEN=$API_TOKEN
ENV BACKEND_HOST=$BACKEND_HOST
ENV BACKEND_PORT=$BACKEND_PORT

CMD ["python", "main.py"]
