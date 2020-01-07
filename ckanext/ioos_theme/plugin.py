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
    except ValueError, TypeError:
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

def convert_date(date_val, check_datetime=False, date_to_datetime=False):
    """Given a * date or datetime string.  Optionally checks the type parsed
       of the parsed value prior to being returned as a string"""
    utc = pendulum.timezone("UTC")
    if date_val is None or date_val == '*':
        if check_datetime:
            raise ValueError("Value is not datetime")
        return '*'
    else:
        d_raw = pendulum.parsing.parse_iso8601(date_val.strip())
        if (check_datetime and not isinstance(d_raw, datetime.datetime) and
            not date_to_datetime):
            raise ValueError("Value is not datetime")
        if isinstance(d_raw, datetime.datetime):
            pendulum_date = utc.convert(pendulum.instance(d_raw))
            # need to truncate/eliminate microseconds in order to work with solr
            if pendulum_date.microsecond == 0:
               return pendulum_date.to_iso8601_string()
            else:
                log.info("Datetime has nonzero microseconds, truncating to "
                         "zero for compatibility with Solr")
                return pendulum_date.replace(microsecond=0).to_iso8601_string()
        # if not a datetime, then it's a date
        elif isinstance(d_raw, datetime.date):
            if date_to_datetime:
                # any more elegant way to achieve conversion to datetime?
                dt_force = datetime.datetime.combine(d_raw,
                                                datetime.datetime.min.time())
                # probably don't strictly need tz argument, but doesn't hurt
                # to be explicit
                new_dt_str = pendulum.instance(dt_force,
                                               tz=utc).to_iso8601_string()
                log.info("Converted date {} to datetime {}".format(
                            d_raw.isoformat(), new_dt_str))
                return new_dt_str
            else:
               return d_raw.isoformat()

        else:
            # probably won't reach here, but not a bad idea to be defensive anyhow
            raise ValueError("Type {} is not handled by the datetime conversion routine")

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

def gcmd_keywords_to_multilevel_sorted_dict(gcmd_keywords):

    gcmd_dict = SortedDict()
    prepped_kw = (re.sub(r"\s*>\s*", ' > ', re.sub(r"\s+", " ", kw)).upper()
                  for kw in gcmd_keywords)
    # put into multilevel sorted dict.  Could possibly subclass defaultdict
    # for this?
    for kw in prepped_kw:
        gcmd_levels = kw.split(' > ')
        current_hierarchy = gcmd_dict
        for level in gcmd_levels:
            if level not in current_hierarchy:
                current_hierarchy[level] = SortedDict()
            current_hierarchy = current_hierarchy[level]

    # now generate
    return gcmd_dict

def gcmd_generate(gcmd_keywords):
    return gcmd_to_ul(gcmd_keywords_to_multilevel_sorted_dict(gcmd_keywords))

def gcmd_to_ul(gcmd_dict, elem=None, prev_results=None):
    # avoid side effects with mutable args duplicating same tree several times
    if prev_results is None:
        prev_results = []
    if elem is None:
        elem = etree.Element('ul', {'class': 'tag-list tree'})
    for sub_key, sub_dict in gcmd_dict.items():
        gcmd_list = etree.SubElement(elem, 'li')
        new_hier = prev_results + [sub_key]
        exploded_kw = " > ".join(new_hier)
        gcmd_link = etree.SubElement(gcmd_list, 'a',
                                     {'class': 'tag',
                                      'href': '/dataset?q=gcmd_keywords:"{}"'.format(exploded_kw)})
        gcmd_link.text = sub_key
        if sub_dict:
            new_ul = etree.SubElement(gcmd_list, 'ul', {'class': 'tag-list'})
            gcmd_to_ul(sub_dict, new_ul, new_hier)

    # operates on side effects, so if the base recursion case, return
    # the generated XML string.
    if not prev_results:
        return etree.tostring(elem, pretty_print=True)


def split_gcmd_tags(tags):
    """
    Splits any GCMD keyword components (usually separated by " > " into
    separate, unique tags. Returns a list of tags if successful, or None
    if the tags ran into an exception
    """
    #TODO: should we also store the full GCMD keywords as extras and in
    #           Solr?
    try:
        unique_tags = set(chain(*[re.split(r'\s*>\s*', t.strip()) for t
                                    in tags]))
        # limit tags to 100 chars so we don't get a database error
        return [{'name': val[:100]} for val in sorted(unique_tags)]
    except:
        log.exception("Error occurred while splitting GCMD tags:")
        return None

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

    def before_index(self, data_dict):
        data_modified = copy.deepcopy(data_dict)
        start_end_time = []
        responsible_party = data_dict.get('extras_responsible-party')
        if responsible_party is not None:
            originators = get_originator_names(responsible_party)
            if len(originators) > 0:
                data_modified['data_provider'] = originators

        gcmd_keywords = data_dict.get('extras_gcmd_keywords')
        if gcmd_keywords is not None:
            try:
                gcmd_keywords_parse = [e.strip() for e in
                                       json.loads(gcmd_keywords)]
            except ValueError:
                log.exception("Can't parse GCMD keywords from JSON")
            else:
                data_modified['gcmd_keywords_full'] = gcmd_keywords_parse

        for field in ('temporal-extent-begin', 'temporal-extent-end'):
            if field in data_dict:
                log.debug("Found time for field {}: {}".format(field, data_dict[field]))
                # "now" is probably not strictly valid ISO 19139 but it occurs
                # fairly often
                if data_dict.get(field, '').lower() == 'now':
                    log.info("Converting 'now' to current date and time")
                    utc = pendulum.timezone("UTC")
                    parsed_val = pendulum.now(utc).replace(
                                        microsecond=0).to_iso8601_string()
                else:
                    try:
                        # TODO: Add some sane support for indeterminate dates
                        parsed_val = convert_date(data_dict[field], True, True)
                    except ValueError, pendulum.parsing.exceptions.ParserError:
                        log.exception("data_dict[field] does not convert to "
                                        "datetime, skipping storage of temporal "
                                        "extents into Solr")
                        return data_dict
                start_end_time.append(parsed_val)

        if len(start_end_time) == 2:
            # format to solr DateRangeField
            data_modified["temporal_extent"] = "[{} TO {}]".format(*start_end_time)
        # should this even be possible to reach?
        elif len(start_end_time) == 1:
            data_modified["temporal_extent"] = start_end_time[0]

        # Solr StringField max length is 32766 bytes.  Truncate to this length
        # if any field exceeds this length so that harvesting doesn't crash
        max_solr_strlen_bytes = 32766
        for extra_key, extra_val in data_modified.iteritems():
            if (extra_key not in {'data_dict', 'validated_data_dict'} and
                isinstance(extra_val, six.string_types)):
                bytes_str = extra_val.encode("utf-8")
                bytes_len = len(bytes_str)
                # TODO: if json, ignore
                if bytes_len > max_solr_strlen_bytes:
                    log.info("Key {} length of {} bytes exceeds maximum of {}, "
                             "truncating string".format(extra_key,
                                                        max_solr_strlen_bytes,
                                                        bytes_len))
                    trunc_val = bytes_str[:max_solr_strlen_bytes].decode('utf-8',
                                                                         'ignore')
                    data_modified[extra_key] = trunc_val

        log.debug(data_modified.get('temporal_extent'))
        return data_modified

    def before_search(self, search_params):
        search_params_modified = copy.deepcopy(search_params)



        if 'extras' in search_params:
            extras = search_params['extras']
            begin_time = extras.get('ext_timerange_start')
            end_time = extras.get('ext_timerange_end')
            # temporal handling
            # if both begin and end time are none, no search window was provided
            if begin_time is None and end_time is None:
                return search_params
            else:
                try:
                    log.debug(begin_time)
                    convert_begin = convert_date(begin_time)
                    log.debug(convert_begin)
                    log.debug(end_time)
                    convert_end = convert_date(end_time)
                    log.debug(convert_end)
                except pendulum.parsing.exceptions.ParserError:
                    log.exception("Error while parsing begin/end time")
                    raise SearchError("Cannot parse provided time")


                log.debug(search_params)
                # fq should be defined in query params, but just in case, use .get
                # defaulting to empty string
                fq_contents = search_params.get('fq', '')
                fq_modified = ("{} +temporal_extent:[{} TO {}]".format(
                                fq_contents, convert_begin, convert_end))

                search_params_modified['fq'] = fq_modified
                log.debug(search_params_modified)
                return search_params_modified

    # IFacets

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
            "gcmd_generate": gcmd_generate,
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
        map.connect('ckanadmin_index', '/ckan-admin', controller=admin_controller,
                    action='index', ckan_icon='legal')
        map.connect('ckanadmin_config', '/ckan-admin/config', controller=admin_controller,
                    action='config', ckan_icon='check')
        map.connect('ckanadmin_trash', '/ckan-admin/trash', controller=admin_controller,
                    action='trash', ckan_icon='trash')
        map.connect('ckanadmin', '/ckan-admin/{action}', controller=admin_controller)

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
            'feedback.recipients': [unicode],
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
