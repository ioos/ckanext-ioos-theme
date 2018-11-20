#!/usr/bin/env python
'''
ckanext/ioos_theme/controllers/feedback.py

IOOS Theme Feedback Controller
'''
from ckan.lib.base import BaseController, render, _
from ckan.lib import helpers as h
from ckan.common import request
from ckanext.ioos_theme.lib import feedback


class FeedbackController(BaseController):
    '''
    The FeedbackController renders a Feedback Form and accepts an HTTP POST to
    /feedback with the Form parameters. On a POST it will flash a notice
    thanking the user for their feedback and then redirect to the home page.
    '''

    def index(self, data=None, errors=None, error_summary=None):
        '''
        Returns a render for the feedback form.

        :param dict data: Unused
        :param dict errors: Any validation errors that the user has entered
                            will be passed to the controller
        :param dict error_summary: Summary of any validation errors
        '''
        # If the HTTP request is POST
        if request.params:
            return self._post_feedback()

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {
            'package_name': None,
            'data': data,
            'errors': errors,
            'error_summary': error_summary
        }
        return render('feedback/form.html', extra_vars=vars)

    def feedback_package(self, package_name=None, data=None, errors=None,
                         error_summary=None):
        '''
        Returns a render for the feedback form.

        :param dict data: Unused
        :param dict errors: Any validation errors that the user has entered
                            will be passed to the controller
        :param dict error_summary: Summary of any validation errors
        '''
        # If the HTTP request is POST
        if request.params:
            return self._post_feedback()

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {
            'package_name': package_name,
            'data': data,
            'errors': errors,
            'error_summary': error_summary
        }
        return render('feedback/form.html', extra_vars=vars)

    def _post_feedback(self):
        '''
        Redirects the user to the home page and flashes a message,
        acknowledging the feedback.
        '''
        context = {
            'name': request.params['name'],
            'email': request.params['email'],
            'feedback': request.params['feedback'],
            'package_name': request.params.get('package_name'),
            'referrer': request.referrer
        }
        feedback.send_feedback(context)
        h.flash_notice(_('Thank you for your feedback'))
        if context['package_name'] is None:
            h.redirect_to(controller='home', action='index')
        else:
            h.redirect_to(controller='package', action='read', id=context['package_name'])
        return
