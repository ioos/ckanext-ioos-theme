FROM ckan/ckan

# Install git
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y git libgeos-dev libxml2-dev libxslt1-dev supervisor postgresql-client

# Install the CKAN Spatial extension
RUN $CKAN_HOME/bin/pip install -e git+https://github.com/lukecampbell/ckanext-spatial.git@deploy#egg=ckanext-spatial
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckanext-spatial/pip-requirements.txt

RUN $CKAN_HOME/bin/pip install -e git+https://github.com/lukecampbell/ckanext-harvest.git@master#egg=ckanext-harvest
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckanext-harvest/pip-requirements.txt

RUN $CKAN_HOME/bin/pip install -e git+https://github.com/lukecampbell/pycsw.git@ckan#egg=pycsw
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/pycsw/requirements.txt

ADD ./ckanext-ioos_theme $CKAN_HOME/src/ckanext-ioos_theme
RUN $CKAN_HOME/bin/pip install -e $CKAN_HOME/src/ckanext-ioos_theme

# Set CKAN_INIT 
ENV CKAN_INIT="true"


# Add my custom configuration file
ADD ./contrib/docker/my_init.d /etc/my_init.d
ADD ./contrib/supervisor/conf.d /etc/supervisor/conf.d

# Add services
ADD ./contrib/docker/services /etc/service
