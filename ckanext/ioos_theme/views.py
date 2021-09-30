from flask import Blueprint, make_response

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

    def before_map(self, map):
        '''
        Defines routes for feedback and overrides routes for the admin controller
        '''
        controller = 'ckanext.ioos_theme.controllers.feedback:FeedbackController'
        map.connect('feedback_package', '/feedback/{package_name}', controller=controller, action='index', package_name='{package_name}')
        map.connect('feedback', '/feedback', controller=controller, action='index')

        admin_controller = 'ckanext.ioos_theme.controllers.admin:IOOSAdminController'
        map.connect('admin.index', '/ckan-admin', controller=admin_controller,
                    action='index', ckan_icon='legal')
        map.connect('admin.config', '/ckan-admin/config', controller=admin_controller,
                    action='config', ckan_icon='check')
        map.connect('admin.trash', '/ckan-admin/trash', controller=admin_controller,
                    action='trash', ckan_icon='trash')
        map.connect('admin', '/ckan-admin/{action}', controller=admin_controller)

        csw_controller = 'ckanext.ioos_theme.controllers.csw:CswController'
        map.connect('csw_admin', '/admin/csw', controller=csw_controller,
                    action='index', ckan_icon='gear')
        map.connect('csw_clear', '/admin/csw/clear',
                    controller=csw_controller, action='clear')
        map.connect('csw_sync', '/admin/csw/sync',
                    controller=csw_controller, action='sync')

        return map
