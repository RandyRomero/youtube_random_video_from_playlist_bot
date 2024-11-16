FROM python:3.12.5-slim-bookworm

RUN apt-get update \
    && apt-get -y install gcc libpq-dev

WORKDIR src

COPY requirements.txt requirements-dev.txt ./

RUN pip install -U pip \
    && pip install uv \
	&& uv venv \
	&& . .venv/bin/activate \
	&& uv pip install -r requirements-dev.txt

COPY . .

CMD ["python", "main.py"]