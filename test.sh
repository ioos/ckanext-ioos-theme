#!/bin/bash
export DATABASE_URL=postgresql://ckan:ckan@192.168.99.100/ckan


docker build -t lukecampbell/docker-ioos-catalog . && \
docker run -i -t --name "docker-ioos-catalog-test" \
    -e DATABASE_URL=$DATABASE_URL \
    --link solr:solr \
    --link redis:redis \
    -p 80:80 \
    lukecampbell/docker-ioos-catalog
docker rm docker-ioos-catalog-test
