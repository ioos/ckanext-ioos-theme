#!/usr/bin/env python
'''
ckanext/ioos_theme/controllers/admin.py

IOOS Theme Admin Controller
'''
from ckan.controllers.admin import AdminController
from ckan.lib import base

_ = base._


class IOOSAdminController(AdminController):
    '''
    This is a subclass of the original AdminController but it changes the order
    of the configuration items and adds a new one for feedback.
    '''

    def _get_config_form_items(self):
        '''
        Returns a modified list of the original items list
        '''
        # Styles for use in the form.select() macro.
        styles = [{'text': 'Default', 'value': '/base/css/main.css'},
                  {'text': 'Red', 'value': '/base/css/red.css'},
                  {'text': 'Green', 'value': '/base/css/green.css'},
                  {'text': 'Maroon', 'value': '/base/css/maroon.css'},
                  {'text': 'Fuchsia', 'value': '/base/css/fuchsia.css'}]

        homepages = [{'value': '1', 'text': 'Introductory area, search, featured group and featured organization'},
                     {'value': '2', 'text': 'Search, stats, introductory area, featured organization and featured group'},
                     {'value': '3', 'text': 'Search, introductory area and stats'}]

        items = [
            {'name': 'ckan.site_title', 'control': 'input', 'label': _('Site Title'), 'placeholder': ''},
            {'name': 'ckan.main_css', 'control': 'select', 'options': styles, 'label': _('Style'), 'placeholder': ''},
            {'name': 'ckan.site_description', 'control': 'input', 'label': _('Site Tag Line'), 'placeholder': ''},
            {'name': 'ckan.site_logo', 'control': 'input', 'label': _('Site Tag Logo'), 'placeholder': ''},
            {'name': 'ckan.site_about', 'control': 'markdown', 'label': _('About'), 'placeholder': _('About page text')},
            {'name': 'ckan.site_intro_text', 'control': 'markdown', 'label': _('Intro Text'), 'placeholder': _('Text on home page')},
            {'name': 'ckan.site_custom_css', 'control': 'textarea', 'label': _('Custom CSS'), 'placeholder': _('Customisable css inserted into the page header')},
            {'name': 'ckan.homepage_style', 'control': 'select', 'options': homepages, 'label': _('Homepage'), 'placeholder': ''},
            {'name': 'smtp.server', 'control': 'input', 'label': _('SMTP Server'), 'placeholder': ''},
            {'name': 'smtp.port', 'control': 'input', 'label': _('SMTP PORT'), 'placeholder': ''},
            {'name': 'smtp.starttls', 'control': 'checkbox', 'label': _('TLS Enabled'), 'placeholder': ''},
            {'name': 'smtp.user', 'control': 'input', 'label': _('SMTP User'), 'placeholder': ''},
            {'name': 'smtp.password', 'control': 'input', 'label': _('SMTP Password'), 'placeholder': ''},
            {'name': 'smtp.mail_from', 'control': 'input', 'label': _('Mail From'), 'placeholder': ''},
        ]
        items.extend([
            {
                'name': 'feedback.recipients',
                'control': 'input',
                'label': _('Feedback Recipients'),
                'placeholder': ''
            }
        ])
        return items
