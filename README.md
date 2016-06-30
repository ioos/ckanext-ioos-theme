[![Stories in Ready](https://badge.waffle.io/ioos/catalog-ckan.png?label=ready&title=Ready)](https://waffle.io/ioos/catalog-ckan)
# catalog-ckan

The IOOS CKAN Catalog

# Setup

This setup presumes that docker is successfully installed on the host and any virtual machines or hosts are running.


1. Create a network for our containers to run in
   ```
   docker network create catalog
   ```

2. Create an environment file called `env` with the container settings:
   ```
   POSTGRES_USER=ckanadmin
   POSTGRES_PASSWORD=ckanpass
   POSTGRES_DB=ckan
   POSTGRES_HOST=postgis
   POSTGRES_PORT=5432
   CKAN_INIT=true
   REDIS_URL=redis://redis/5
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_DB=5
   SOLR_HOST=solr
   SOLR_PORT=8983
   CKAN_DEBUG=false
   ```

3. Launch solr as a daemon
   ```
   docker run --net catalog --name solr -d lukecampbell/docker-ckan-solr
   ```

4. Launch PostGIS
   ```
   docker run --net catalog --name postgis -d --env-file env mdillon/postgis:9.3
   ```

5. Launch redis
   ```
   docker run --net catalog --name redis -d redis:3.0.7-alpine
   ```

6. Launch the CKAN container

    ```
    docker run --net catalog --name ckan -p 8080:8080 --env-file env -d ioos/catalog-docker-ckan
    ```

7. Launch the harvester container

    ```
    docker run --net catalog --name harvester --env-file env -d ioos/catalog-docker-ckan-harvester
    ```

8. Launch the PyCSW container

    ```
    docker run --net catalog --name pycsw -p 8081:8080 --env-file env -d ioos/catalog-docker-pycsw
    ```

# Setup with `docker-compose`

Alternatively, all the components can be fetched for a single server using `docker-compose`.
The Solr and PostgreSQL containers also have named volumes in order to persist data in between restarts.
First, set the environment variables in a file called `env`, see step 2 above.


1. Create a named volume for the PostGIS data
   ```
   docker volume create --name pg_data
   ```

2. Create a named volume for the solr data
   ```
   docker volume create --name solr_core_data
   ```

3. Run `docker-compose up` and the containers should build.

CKAN will then be running and exposed on port 8080 for that host. PyCSW will be
running on port 8081. Every hour PyCSW will synchronize to CKAN.

# Usage

Once the containers are launched you should be able to access the CKAN instance by visiting port 8080



