FROM ioos/ckanext-ioos-theme:base

COPY ./contrib/my_init.d /etc/my_init.d

RUN echo "Listen 8080" > /etc/apache2/ports.conf

COPY ./contrib/config/ckan-apache.conf /etc/apache2/sites-available/ckan_default.conf

RUN a2ensite ckan_default
RUN a2dissite 000-default

CMD ["/sbin/my_init", "--", "/bin/services/ckan/run"]
