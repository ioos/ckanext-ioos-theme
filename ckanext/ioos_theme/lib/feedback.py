#!/usr/bin/env python
'''
ckanext/ioos_theme/lib/feedback.py

Send feedback email
'''
from ckan.lib.base import render
from ckan.lib.mailer import mail_recipient

import logging
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


def send_feedback(context):
    '''
    Sends a feedback message to the recipients in the feedback.recipients
    config list.

    :param dict context: A dictionary containing the name, email and feedback
                         from a user.
    '''

    body = render('emails/feedback.txt', context)
    subject = 'IOOS Catalog Feedback'

    recipients_str = toolkit.config.get('feedback.recipients')
    if not recipients_str:
        log.info("No recipients specified, feedback email not sent")
        return
    for recipient in recipients_str.split(' '):
        mail_recipient('', recipient, subject, body)
