FROM ckan/ckan

# Install git
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y git libgeos-dev libxml2-dev libxslt1-dev supervisor postgresql-client

# Install the CKAN Spatial extension
# CKAN spatial extension has no tagged Git releases currently, so freeze the
# version at a known good commit to prevent breakage from later versions
RUN $CKAN_HOME/bin/pip install -e git+https://github.com/ckan/ckanext-spatial.git@stable#egg=ckanext-spatial
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckanext-spatial/pip-requirements.txt

# must use this commit or similar as tagged versions cause "Add harvests" page
# to display no fields
RUN $CKAN_HOME/bin/pip install -e git+https://github.com/ckan/ckanext-harvest.git@7f506913f8e789#egg=ckanext-harvest
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckanext-harvest/pip-requirements.txt

RUN $CKAN_HOME/bin/pip install -e git+https://github.com/geopython/pycsw.git@1.10.4#egg=pycsw
RUN $CKAN_HOME/bin/pip install -r $CKAN_HOME/src/pycsw/requirements.txt

ADD ./ckanext-ioos_theme $CKAN_HOME/src/ckanext-ioos_theme
RUN $CKAN_HOME/bin/pip install -e $CKAN_HOME/src/ckanext-ioos_theme

# Set CKAN_INIT 
ENV CKAN_INIT="true"


# Add my custom configuration file
ADD ./contrib/config/pycsw/default.cfg $CKAN_HOME/src/pycsw/default.cfg
ADD ./contrib/config/pycsw/pycsw.wsgi $CKAN_CONFIG/pycsw.wsgi

ADD ./contrib/docker/apache.conf /etc/apache2/sites-available/ckan_default.conf
RUN echo "Listen 8080\nListen 8081" > /etc/apache2/ports.conf
RUN a2ensite ckan_default
RUN a2dissite 000-default

# Configure nginx
ADD ./contrib/docker/nginx.conf /etc/nginx/nginx.conf

ADD ./contrib/docker/my_init.d /etc/my_init.d
ADD ./contrib/supervisor/conf.d /etc/supervisor/conf.d

# Add services
ADD ./contrib/docker/services /etc/service

# run the init script
CMD /sbin/my_init
