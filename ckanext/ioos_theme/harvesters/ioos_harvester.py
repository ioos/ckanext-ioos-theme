#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ckan.plugins as p
import logging
from ckanext.spatial.harvesters.base import SpatialHarvester
from ckanext.spatial.interfaces import ISpatialHarvester
import json
from itertools import groupby
from inflection import titleize
from collections import OrderedDict

log = logging.getLogger(__name__)


class IOOSHarvester(SpatialHarvester):

    def get_package_dict(self, iso_values, harvest_object):
        '''
        '''
        package_dict = SpatialHarvester.get_package_dict(self, iso_values, harvest_object)
        simple_keys = {'publisher_info', 'resource-provider',
                       'distributor-info', 'aggregation-info',
                       'additional-information-source', 'purpose',
                       # Constraints
                       'use-constraints', 'access-constraints', 'fees',
                       # lineage
                       'lineage', 'lineage-process-steps'}
        extras = {k: iso_values.get(k) for k in simple_keys if k in iso_values}

        # sort keywords according to thesaurus name
        iso_values['keywords'].sort(key=lambda x: (x['type'] == '', x['type'],
                                                  x['thesaurus']['title'] != '',
                                                   x['thesaurus']['title']))
        group_sort_func = lambda x: (x['type'] == '', x['type'])
        # group by theme keyword
        extras['grouped_keywords'] = OrderedDict(
                                          [(titleize(k[1] if not k[0] else
                                               'Uncategorized') + ' Keywords',
                                           list(g)) for k, g in
                                           groupby(iso_values['keywords'],
                                                   group_sort_func)]
                                     )

        if iso_values.get('publisher', None):
            extras['publisher'] = iso_values.get('publisher', [])
        if iso_values.get('dataset-edition'):
            extras['dataset-edition'] = iso_values['dataset-edition']
            package_dict["version"] = iso_values['dataset-edition'][0]
        if iso_values.get('presentation-form'):
            extras['presentation-form'] = iso_values['presentation-form'][0]
        if iso_values.get('responsible-organisation'):
            log.info("Checking for responsible-organisation")
            extras['responsible-organisation'] = iso_values.get('responsible-organisation', [])

        extras_kv = [{'key': k,
                      'value': json.dumps(v) if isinstance(v, (list, dict))
                               else v} for k, v in extras.iteritems()]

        package_dict['extras'] = package_dict['extras'] + extras_kv

        return package_dict
