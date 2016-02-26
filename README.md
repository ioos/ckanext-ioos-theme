# docker-ioos-catalog

Docker image for IOOS Catalog comprising CKAN+PyCSW+Harvesting

# Setup

This setup presumes that docker is successfully installed on the host and any virtual machines or hosts are running.

1. Get the solr image
   ```
   docker pull lukecampbell/docker-ckan-solr
   ```

2. Launch solr
   ```
   docker run --name "solr" -d lukecampbell/docker-ckan-solr
   ```

3. Get the postgis image if you want to run PostGIS in a container.
  
   __Note: It's generally advised to run the database on a dedicated host for production settings__

   ```
   docker pull lukecampbell/docker-ckan-postgis
   ```

4. Launch PostGIS

   ```
   docker run --name "postgis" -p 5432:5432 -d -t -e "POSTGRES_USER=ckanadmin" -e "POSTGRES_PASS=ckanadmin" -e "POSTGRES_DB=ckan" lukecampbell/docker-postgis
   ```

5. Get the redis image
   ```
   docker pull redis
   ```

6. Launch redis
   ```
   docker run --name redis -d redis
   ```

7. Pull the IOOS CKAN image
   ```
   docker pull lukecampbell/docker-ioos-catalog
   ```

8. Launch the CKAN container

    ```
    docker run --name "ioos-catalog" \
      -e "DATABASE_URL=postgresql://ckan:ckanpass@192.168.99.100/ckan" \
      --link solr:solr \
      --link redis:redis \
      --link postgis:db \
      -p 80:80 \
      -d -t \
      lukecampbell/docker-ioos-catalog
    ```



# Usage

Once the containers are launched you should be able to access the CKAN instance by visiting port 80



