FROM python:3.9-slim

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/opt/app/src:/opt/app/test"
ENV MODAK_CONFIG "/opt/app/conf/dock-iac-model.ini"
CMD ["python", "app/app.py"]
