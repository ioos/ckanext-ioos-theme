#!/bin/bash
export CKAN_INIT=true

if [[ -n $1 ]]; then 
    LAUNCHOPTS=$1
else
    LAUNCHOPTS=/sbin/my_init
fi

echo "Launching container with $LAUNCHOPTS"

docker build -t lukecampbell/docker-ioos-catalog . && \
docker run -i -t --name "docker-ioos-catalog-test" \
    -e CKAN_INIT=$CKAN_INIT \
    -e CKAN_DEBUG=$CKAN_DEBUG \
    --link solr:solr \
    --link redis:redis \
    --link postgis:db \
    -p 80:80 \
    lukecampbell/docker-ioos-catalog \
    $LAUNCHOPTS
docker rm docker-ioos-catalog-test
