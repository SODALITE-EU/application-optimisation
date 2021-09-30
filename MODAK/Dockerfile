FROM python:3.9-slim

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN db/tosqlite.py -C db/

VOLUME /opt/app/db

ENV PYTHONPATH "${PYTHONPATH}:/opt/app"
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--access-logfile", "-", "MODAK.app:app"]
