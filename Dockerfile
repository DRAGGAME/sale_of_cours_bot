FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

#RUN python3 -m venv venv
#
#ENV PATH="/app/venv/bin:$PATH"

RUN pip install -r requirements.txt

EXPOSE 5432

COPY . /app

CMD ["python", "run.py"]