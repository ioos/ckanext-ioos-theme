FROM ckan/ckan

# Install git
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y git libgeos-dev libxml2-dev libxslt1-dev

# Install the CKAN Spatial extension
RUN $CKAN_HOME/bin/pip install -e git+https://github.com/ckan/ckanext-spatial.git@stable#egg=ckanext-spatial
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckanext-spatial/pip-requirements.txt

RUN $CKAN_HOME/bin/pip install -e git+https://github.com/ckan/ckanext-harvest.git@stable#egg=ckanext-harvest
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckanext-harvest/pip-requirements.txt


# Add my custom configuration file
ADD ./contrib/docker/my_init.d /etc/my_init.d
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

