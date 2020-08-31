# MODAK install

Login to VM on which you want to deploy

```
git clone https://github.com/SODALITE-EU/application-optimisation.git
```

download a Google service account JSON keyfile to  
```
MODAK/conf/modak-f305a35c96dc.json
```
To deploy the API

```
cs MODAK/app
tar -czvf modak.tar.gz -C ../../MODAK .
mv modak.tar.gz pyMODAK/.
docker-compose build --no-cache
docker-compose up
```

Test the deployment using the [examples](EXAMPLE.md)



