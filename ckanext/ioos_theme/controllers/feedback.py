from ckan.lib.base import BaseController, render, _
from ckan.lib import helpers as h
from ckan.common import request
from ckanext.ioos_theme.lib import feedback


class FeedbackController(BaseController):

    def index(self, data=None, errors=None, error_summary=None):
        if request.params:
            context = {
                'name': request.params['name'],
                'email': request.params['email'],
                'feedback': request.params['feedback']
            }
            feedback.send_feedback(context)
            h.flash_notice(_('Thank you for your feedback'))
            h.redirect_to(controller='home', action='index')
            return

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {
            'data': data,
            'errors': errors,
            'error_summary': error_summary
        }
        return render('feedback/form.html', extra_vars=vars)
