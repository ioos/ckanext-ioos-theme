#!/usr/bin/env python
#-*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import json

def get_party(pkg):
    responsible_party = next((extra['value'] for extra in pkg['extras'] if extra['key'] == 'responsible-party'))
    decoded_party = json.loads(responsible_party)
    return decoded_party

def get_responsible_party(pkg):
    responsible_party = get_party(pkg)
    for party in responsible_party:
        if 'name' in party:
            return party['name']

def get_publisher(pkg):
    publishers = next((extra['value'] for extra in pkg['extras'] if extra['key'] == 'publisher' ))
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

def get_responsible_organization(pkg):
    responsible_organization = next((extra['value'] for extra in pkg['extras'] if extra['key'] == 'responsible-organisation'))
    return json.loads(responsible_organization)

class Ioos_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ioos_theme')

    def get_helpers(self):
        return {
            "ioos_theme_get_responsible_party" : get_responsible_party,
            "ioos_theme_get_point_of_contact" : get_point_of_contact,
            "ioos_theme_get_publisher" : get_publisher,
            "ioos_theme_get_responsible_organization" : get_responsible_organization
        }
