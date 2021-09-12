FROM python:3.9-slim

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN db/tosqlite.py -C db/

ENV PYTHONPATH "${PYTHONPATH}:/opt/app/src:/opt/app/test"
CMD ["python", "app/app.py"]
