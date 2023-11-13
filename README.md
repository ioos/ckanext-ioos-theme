# ckanext-ioos-theme

The IOOS Catalog CKAN extension.  For directions on how to build using Docker, please consult the README on https://github.com/ioos/catalog-docker-base

## Features

- Theming of CKAN around IOOS styling
- Date/time and depth (below sea level) search/filter controls
- Faceted filter controls for [CF Standard Name](https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html) and [GCMD Keyword](https://www.earthdata.nasa.gov/learn/find-data/idn/gcmd-keywords) search
- Custom handling of ISO 19115 metadata ingested to provide additional info, such as [IOOS Metadata Profile](https://ioos.github.io/ioos-metadata/ioos-metadata-profile-v1-2.html) metadata from ERDDAP data sources, data providers, CF Standard Names, and GCMD Keywords
