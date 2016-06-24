# docker-ioos-catalog

Docker image for IOOS Catalog comprising CKAN+PyCSW+Harvesting

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
    docker run --net catalog --name ioos-catalog -p 80:80 --env-file env -d ioos/ckanext-ioos-theme
    ```

# Setup with `docker-compose`

Alternatively, all the components can be fetched for a single server using `docker-compose`.
The Solr and PostgreSQL containers also have named volumes in order to persist data in between restarts.
First, set the environment variables in a file called `env`, see step 2 above.


Run `docker-compose up` and the containers should build.  CKAN will be exposed
on port 80 for the host.


# Usage

Once the containers are launched you should be able to access the CKAN instance by visiting port 80



