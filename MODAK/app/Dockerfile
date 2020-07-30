FROM python:3.6
COPY requirements.txt .
RUN pip3 install -r requirements.txt
WORKDIR /home/MODAK
COPY pyMODAK/modak.tar.gz /home/MODAK/.
RUN tar -xvf modak.tar.gz
WORKDIR /home/MODAK/src
ENV PYTHONPATH "${PYTHONPATH}:/home/MODAK/src:/home/MODAK/test"
ENV MODAK_CONFIG "/home/MODAK/conf/dock-iac-model.ini"
CMD ["python3", "../app/app.py"]
