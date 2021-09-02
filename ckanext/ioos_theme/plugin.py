#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
ckanext/ioos_theme/plugin.py

Plugin definition for IOOS Theme
'''

import ckan.plugins as p
from ckan.lib.search import SearchError
from ckan.plugins import toolkit
import json
import logging
from collections import OrderedDict
from ckan.logic.validators import int_validator
from ckanext.spatial.interfaces import ISpatialHarvester
import copy
import pendulum
import datetime
import six
from itertools import chain
import re
from six.moves import urllib
from lxml import etree
from collections import OrderedDict
from sortedcontainers import SortedDict

log = logging.getLogger(__name__)

def get_originator_names(party_text):
    ret_val = []
    try:
        parties = json.loads(party_text)
        for party in parties:
            if 'originator' in party.get('roles', []):
                name = party.get('name')
                # will return True if not empty string or
                # nonexistent key
                if name:
                    ret_val.append(name)
    except (ValueError, TypeError):
        log.exception("Error occured while parsing JSON value")
    return ret_val

def get_party(pkg):
    responsible_party = next((extra['value'] for extra in pkg['extras'] if
                              extra['key'] == 'responsible-party'))
    decoded_party = json.loads(responsible_party)
    return decoded_party

def get_responsible_party(pkg):
    responsible_party = get_party(pkg)
    for party in responsible_party:
        if 'name' in party:
            return party['name']


def get_publisher(pkg):
    publishers = next((extra['value'] for extra in pkg['extras']
                       if extra['key'] == 'publisher'))
    if publishers:
        return json.loads(publishers)
    return []


def get_point_of_contact(pkg):
    responsible_party = get_party(pkg)
    pocs = []
    for party in responsible_party:
        if 'pointOfContact' in party['roles']:
            pocs.append(party['name'])
    return pocs


def get_role_code(role):
    '''
    Returns the Human Readable version of the role from the ISOTC211/19115 role
    list.

    :param str role: Role
    '''
    if role == 'resourceProvider':
        return 'Resource Provider'
    if role == 'custodian':
        return 'Custodian'
    if role == 'owner':
        return 'Owner'
    if role == 'user':
        return 'User'
    if role == 'distributor':
        return 'Distributor'
    if role == 'originator':
        return 'Originator'
    if role == 'pointOfContact':
        return 'Point of Contact'
    if role == 'principalInvestigator':
        return 'Principal Investigator'
    if role == 'processor':
        return 'Processor'
    if role == 'publisher':
        return 'Publisher'
    if role == 'author':
        return 'Author'
    return role


def get_responsible_organization(pkg):
    responsible_organization = next((extra['value'] for extra in pkg['extras'] if extra['key'] == 'responsible-organisation'))
    return json.loads(responsible_organization)


def get_distribution_formats(pkg):
    '''
    Returns a list of dictionaries containing the name and version of available
    distribution formats.
    '''
    retval = []
    distributors = get_pkg_item(pkg, 'distributor-info')
    if distributors is None:
        return retval
    for distributor in distributors:
        if 'data-format' not in distributor:
            continue
        # I don't know how this is possible but it happens to show up as a string...
        if not isinstance(distributor['data-format'], dict):
            continue
        if not distributor['data-format']:
            continue
        name = distributor['data-format'].get('name', None)
        version = distributor['data-format'].get('version', None)
        if not name:
            continue
        retval.append({
            "name": name,
            "version": version
        })

    formats = get_pkg_item(pkg, 'distributor-formats')
    if formats is None:
        return retval
    for dist_format in formats:
        if not dist_format:
            continue
        name = dist_format.get('name', None)
        version = dist_format.get('version', None)
        if not name:
            continue
        retval.append({
            "name": name,
            "version": version
        })
    return retval


def get_pkg_item(pkg, key):
    try:
        pkg_item = next((extra['value'] for extra in pkg['extras'] if extra['key'] == key))
    except StopIteration:
        return None
    if pkg_item:
        return json.loads(pkg_item)
    return None



def get_pkg_ordereddict(pkg, key):
    try:
        pkg_item = next((extra['value'] for extra in pkg['extras'] if extra['key'] == key))
    except StopIteration:
        return {}
    return json.loads(pkg_item, object_pairs_hook=OrderedDict)


def get_pkg_extra(pkg, key):
    try:
        pkg_item = next((extra['value'] for extra in pkg['extras'] if extra['key'] == key))
    except StopIteration:
        return None
    return pkg_item


def jsonpath(obj, path):
    for key in path.split('.'):
        if not isinstance(obj, dict):
            return {}
        obj = obj.get(key, {})
        log.info("OBJ: %s", obj)
    return obj

class Ioos_ThemePlugin(p.SingletonPlugin):
    '''
    Plugin definition for the IOOS Theme
    '''

    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(ISpatialHarvester, inherit=True)
    p.implements(p.IFacets, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        '''
        Extends the templates directory and adds fanstatic.

        :param config_: Passed from CKAN framework
        '''
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ioos_theme')

    # IPackageController

    def dataset_facets(self, facets_dict, package_type):
        facets_dict['data_provider'] = p.toolkit._('Data Providers')
        return facets_dict

    def organization_facets(self, facets_dict, organization_type,
                                    package_type):
            return self.dataset_facets(facets_dict, package_type)

    # ITemplateHelpers

    def get_helpers(self):
        '''
        Defines a set of callable helpers for the JINJA templates.
        '''
        return {
            "ioos_theme_get_responsible_party": get_responsible_party,
            "ioos_theme_get_point_of_contact": get_point_of_contact,
            "ioos_theme_get_distribution_formats": get_distribution_formats,
            "ioos_theme_get_publisher": get_publisher,
            "ioos_theme_get_responsible_organization": get_responsible_organization,
            "ioos_theme_get_pkg_item": get_pkg_item,
            "ioos_theme_get_pkg_extra": get_pkg_extra,
            "ioos_theme_get_pkg_ordereddict": get_pkg_ordereddict,
            "ioos_theme_jsonpath": jsonpath,
            "ioos_theme_get_role_code": get_role_code,
        }

    # IRoutes

    def before_map(self, map):
        '''
        Defines routes for feedback and overrides routes for the admin controller
        '''
        controller = 'ckanext.ioos_theme.controllers.feedback:FeedbackController'
        map.connect('feedback_package', '/feedback/{package_name}', controller=controller, action='index', package_name='{package_name}')
        map.connect('feedback', '/feedback', controller=controller, action='index')

        admin_controller = 'ckanext.ioos_theme.controllers.admin:IOOSAdminController'
        map.connect('admin_index', '/ckan-admin', controller=admin_controller,
                    action='index', ckan_icon='legal')
        map.connect('admin_config', '/ckan-admin/config', controller=admin_controller,
                    action='config', ckan_icon='check')
        map.connect('admin_trash', '/ckan-admin/trash', controller=admin_controller,
                    action='trash', ckan_icon='trash')
        map.connect('admin', '/ckan-admin/{action}', controller=admin_controller)

        csw_controller = 'ckanext.ioos_theme.controllers.csw:CswController'
        map.connect('csw_admin', '/admin/csw', controller=csw_controller, action='index', ckan_icon='gear')
        map.connect('csw_clear', '/admin/csw/clear', controller=csw_controller, action='clear')
        map.connect('csw_sync', '/admin/csw/sync', controller=csw_controller, action='sync')

        return map

    def update_config_schema(self, schema):
        '''
        Adds two schema items to the config schema, feedback.recipients and
        smtp.port

        :param schema: Passed in from CKAN framework
        '''
        schema.update({
            'feedback.recipients': [str],
            'smtp.port': [int_validator]
        })
        return schema

    def get_package_dict(self, context, data_dict):

        package_dict = data_dict['package_dict']
        iso_values = data_dict['iso_values']

        returned_tags =  split_gcmd_tags(iso_values['tags'])
        if returned_tags is not None:
            package_dict['tags'] = returned_tags

        # ckanext-dcat uses temporal_start and temporal_end for time extents
        # instead of temporal-extent-begin and temporal-extent-end as used by
        # CKAN
        time_pairs = (('temporal_start', 'temporal-extent-begin'),
                      ('temporal_end', 'temporal-extent-end'))
        for new_key, iso_time_field in time_pairs:
            # recreating ckanext-spatial's logic here
            if len(iso_values.get(iso_time_field, [])) > 0:
                package_dict['extras'].append(
                    {'key': new_key, 'value': iso_values[iso_time_field][0]})

        return package_dict
