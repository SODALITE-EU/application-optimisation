FROM mysql:8 as builder
# Example taken from https://github.com/lindycoder/prepopulated-mysql-container-example

# That file does the DB initialization but also runs mysql daemon, by removing the last line it will only init
RUN ["sed", "-i", "s/exec \"$@\"/echo \"not running $@\"/", "/usr/local/bin/docker-entrypoint.sh"]
# needed for intialization
ENV MYSQL_ROOT_PASSWORD=my-secret-pw
COPY modak_mysqldump.sql /docker-entrypoint-initdb.d/
# Need to change the datadir to something else that /var/lib/mysql because the parent docker file defines it as a volume.
# https://docs.docker.com/engine/reference/builder/#volume :
#       Changing the volume from within the Dockerfile: If any build steps change the data within the volume after
#       it has been declared, those changes will be discarded.
RUN ["/usr/local/bin/docker-entrypoint.sh", "mysqld", "--datadir", "/initialized-db"]

FROM mysql:8
COPY --from=builder /initialized-db /var/lib/mysql
RUN apt-get update
RUN apt-get -y install  python3 python3-pip git vim wget
RUN pip3 install --upgrade pip
RUN pip3 install -U pip six wheel setuptools mock 'future>=0.17.1'
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN mkdir /IO
WORKDIR /home/MODAK
COPY modak.tar.gz /home/MODAK/.
RUN tar -xvf modak.tar.gz
WORKDIR /home/MODAK/src
ENV PYTHONPATH "${PYTHONPATH}:/home/MODAK/src:/home/MODAK/test"
ENV MODAK_CONFIG "/home/MODAK/conf/dock-iac-model.ini"
