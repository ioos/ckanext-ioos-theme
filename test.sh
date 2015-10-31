#!/bin/bash
export DATABASE_URL=postgresql://ckan:ckan@192.168.99.100/ckan
export CKAN_INIT=false

if [[ -n $1 ]]; then 
    LAUNCHOPTS=$1
else
    LAUNCHOPTS=/sbin/my_init
fi

echo "Launching container with $LAUNCHOPTS"

docker build -t lukecampbell/docker-ioos-catalog . && \
docker run -i -t --name "docker-ioos-catalog-test" \
    -e DATABASE_URL=$DATABASE_URL \
    -e CKAN_INIT=$CKAN_INIT \
    -e CKAN_DEBUG=$CKAN_DEBUG \
    --link solr:solr \
    --link redis:redis \
    -p 80:80 \
    lukecampbell/docker-ioos-catalog \
    $LAUNCHOPTS
docker rm docker-ioos-catalog-test
