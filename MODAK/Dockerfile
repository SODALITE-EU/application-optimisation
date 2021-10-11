FROM python:3.9-slim

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .
RUN db/tosqlite.py -C db/

VOLUME /opt/app/db

EXPOSE 5000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000", "--access-log", "MODAK.app:app"]
