FROM ioos/ckanext-ioos-theme:base

COPY ./contrib/my_init.d /etc/my_init.d

CMD ["/sbin/my_init", "--", "/bin/services/harvester/run"]

