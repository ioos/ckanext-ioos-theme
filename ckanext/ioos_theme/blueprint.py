from flask import Blueprint, jsonify, make_response
import logging
import urllib.request, urllib.error, urllib.parse
from ckanext.ioos_theme.lib.feedback import send_feedback
from ckan.lib import helpers as h
from ckan.plugins.toolkit import _

import json

from ckan.lib.base import render
from ckan.plugins import toolkit

ioos_bp = Blueprint("ioos_theme",
                    __name__,
                    url_defaults={})

@ioos_bp.route("/feedback", methods=["GET", "POST"])
def feedback(data=None, errors=None, error_summary=None,
             package_name=None):
    '''
    Returns a render for the feedback form.

    :param dict data: Unused
    :param dict errors: Any validation errors that the user has entered
                        will be passed to the controller
    :param dict error_summary: Summary of any validation errors
    '''
    name = ""
    email = ""
    feedback = ""

    recaptcha_response = toolkit.request.form.get('g-captcha-token')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': toolkit.config.get('feedback.site_secret', ''),
        'response': recaptcha_response
    }

    url_data = urllib.parse.urlencode(values)
    #req = urllib.request.Request(url, url_data)
    req = urllib.request.Request(f"{url}?{url_data}")
    response = urllib.request.urlopen(req)
    result = json.load(response)

    # If the HTTP request is POST
    if toolkit.request.method == "POST":
        try:
            logging.debug(result)
            if result['success']:
                return _post_feedback()
            else:
                name = toolkit.request.form['name']
                email = toolkit.request.form['email']
                feedback = toolkit.request.form['feedback']
                h.flash_notice(_('Please fill out missing fields below.'))
        except KeyError:
            name = toolkit.request.args['name']
            email = toolkit.request.args['email']
            feedback = toolkit.request.args['feedback']
            h.flash_notice(_('Please fill out missing fields below.'))

    data = data or {"name": "", "email": "", "feedback": ""}
    data['name'] = name or ""
    data['email'] = email or ""
    data['feedback'] = feedback or ""
    errors = errors or {}
    error_summary = error_summary or {}
    site_key = toolkit.config.get('feedback.site_key', '')
    token = toolkit.config.get('feedback.g-captcha-token', '')

    if not site_key:
        logging.warning('Administrator must set up feedback.site_key')

    vars = {
        'package_name': package_name,
        'data': data,
        'errors': errors,
        'error_summary': error_summary,
        'feedback_site_key': site_key
    }
    return render('feedback/form.html', extra_vars=vars)

def _post_feedback():
    '''
    Redirects the user to the home page and flashes a message,
    acknowledging the feedback.
    '''
    context = {
        'name': toolkit.request.form['name'],
        'email': toolkit.request.form['email'],
        'feedback': toolkit.request.form['feedback'],
        'package_name': toolkit.request.form.get('package_name'),
        'referrer': toolkit.request.referrer
    }
    send_feedback(context)
    h.flash_notice(_('Thank you for your feedback'))
    if context['package_name'] is None:
        h.redirect_to(controller='home', action='index')
    else:
        h.redirect_to(controller='package', action='read', id=context['package_name'])
    return

def _clear_pycsw(config_path):
    '''
    Loads the PyCSW configuration and runs clear

    :param str config_path: Path to the PyCSW config file
    '''
    from bin import ckan_pycsw
    pycsw_config = ckan_pycsw._load_config(config_path)
    ckan_pycsw.clear(pycsw_config)

def _sync_pycsw(config_path):
    '''
    Loads the PyCSW configuration and runs load

    :param str config_path: Path to the PyCSW config file
    '''
    from bin import ckan_pycsw
    pycsw_config = ckan_pycsw._load_config(config_path)
    ckan_url = pycsw_config.get('ckan', 'url')
    ckan_pycsw.load(pycsw_config, ckan_url)

@ioos_bp.route("/admin/csw")
def csw_index():
    '''
    Return the admin page for CSW
    '''
    return render('csw/admin.html')


@ioos_bp.route("/csw/clear")
def csw_clear():
    '''
    Clears the PyCSW database
    '''
    config_path = config.get('ckan.ioos_theme.pycsw_config')
    if os.path.exists(config_path):
        try:
            _clear_pycsw(config_path)
            h.flash_success(_('PyCSW has been cleared'))
        except Exception:
            h.flash_error('Unable to clear PyCSW, see logs for details')
    else:
        h.flash_error('Config for PyCSW doesn\'t exist')
    h.redirect_to(controller='ckanext.ioos_theme.controllers.csw:CswController', action='index')
    return

@ioos_bp.route("/admin/csw/sync", methods=["POST"])
def csw_sync(self):
    '''
    Loads the PyCSW database from CKAN
    '''
    config_path = config.get('ckan.ioos_theme.pycsw_config')
    if os.path.exists(config_path):
        try:
            self._sync_pycsw(config_path)
            h.flash_success(_('PyCSW has been synchronized'))
        except Exception:
            h.flash_error('Unable to synchronize PyCSW, see logs for details')
    else:
        h.flash_error('Config for PyCSW doesn\'t exist')
    h.redirect_to(controller='ckanext.ioos_theme.controllers.csw:CswController', action='index')
    return

    def feedback_form(errors=None, error_summary=None,
                      package_name=None):
        '''
        Returns a render for the feedback form.

        :param dict errors: Any validation errors that the user has entered
                            will be passed to the controller
        :param dict error_summary: Summary of any validation errors
        '''
        name = ""
        email = ""
        feedback = ""

        recaptcha_response = request.params.get('g-captcha-token')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': config.get('feedback.site_secret', ''),
            'response': recaptcha_response
        }

        url_data = urllib.parse.urlencode(values)
        req = urllib.request.Request(url, url_data)
        response = urllib.request.urlopen(req)
        result = json.load(response)

        # If the HTTP request is POST
        if request.params:
            try:
                # Left for reference during refactor to captcha V3
                #if request.params['g-recaptcha-response']:
                if result['success']:
                    return _post_feedback()
                else:
                    name = request.params['name']
                    email = request.params['email']
                    feedback = request.params['feedback']
                    h.flash_notice(_('Please fill out missing fields below.'))
            except KeyError:
                name = request.params['name']
                email = request.params['email']
                feedback = request.params['feedback']
                h.flash_notice(_('Please fill out missing fields below.'))

        data = data or {"name": "", "email": "", "feedback": ""}
        data['name'] = name or ""
        data['email'] = email or ""
        data['feedback'] = feedback or ""
        errors = errors or {}
        error_summary = error_summary or {}
        site_key = config.get('feedback.site_key', '')
        token = config.get('feedback.g-captcha-token', '')

        if not site_key:
            logging.warning('Administrator must setup feedback.site_key')

        vars = {
            'package_name': package_name,
            'data': data,
            'errors': errors,
            'error_summary': error_summary,
            'feedback_site_key': site_key
        }
        return render('feedback/form.html', extra_vars=vars)


