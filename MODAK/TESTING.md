# Setup

For running the unittests you currently need a MariaDB/MySQL server running,
hence Docker is a requirement for now.

To build the MODAK API container from the locally checked out source code and
bring up the API server together with the database, run the following:

```console
$ docker built -t modakopt/modak:api .
$ docker compose up
```

## Running tests inside the Docker image

The Docker image for now also contains the unittests and the test framework.
You can therefore run the unittests inside it without having to install
a corresponding Python environment on your machine.

Assuming the setup succeeded and that the MODAK API server is running
as `modak_restapi_1` (the default unless you have multiple stacks running):

```console
$ docker exec -ti modak_restapi_1 pytest -v
```

*Note*: to make this work MODAK is using a different configuration file when
running inside the Docker image than when running natively.
Check the `Dockerfile` for more details.

There is also the possibility to run the tests without having to rebuild
the Docker container after a change. Simply add the following lines to the
`docker-compose.yml` file for the the `restapi` service:

```yaml
    volumes:
      - ".:/opt/app"
```

## Running tests directly

You can also run tests directly. You still want to use Docker to get a
running database, though. To install the required packages, we recommend
to use a *virtualenv* (or a *conda env*) since we pin the versions and
to avoid conflicts with other packages.

After activating the environment, install the packages and run the tests:

```console
$ pip install -r requirements.txt
$ PYTHONPATH=src pytest -v
```
