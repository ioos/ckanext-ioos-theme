FROM ckan/ckan

# Install git
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y git libgeos-dev libxml2-dev libxslt1-dev supervisor

# Install the CKAN Spatial extension
RUN $CKAN_HOME/bin/pip install -e git+https://github.com/ckan/ckanext-spatial.git@stable#egg=ckanext-spatial
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckanext-spatial/pip-requirements.txt

RUN $CKAN_HOME/bin/pip install -e git+https://github.com/ckan/ckanext-harvest.git@stable#egg=ckanext-harvest
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckanext-harvest/pip-requirements.txt

ADD ./ckanext-ioos_theme $CKAN_HOME/src/ckanext-ioos_theme
RUN $CKAN_HOME/bin/pip install -e $CKAN_HOME/src/ckanext-ioos_theme

# Set CKAN_INIT 
ENV CKAN_INIT="true"


# Add my custom configuration file
ADD ./contrib/docker/my_init.d /etc/my_init.d
ADD ./contrib/supervisor/conf.d /etc/supervisor/conf.d

# Add services
ADD ./contrib/docker/services /etc/service
