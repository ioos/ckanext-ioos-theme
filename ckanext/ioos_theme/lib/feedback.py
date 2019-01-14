#!/usr/bin/env python
'''
ckanext/ioos_theme/lib/feedback.py

Send feedback email
'''
from ckan.lib.base import render_jinja2
from ckanext.ioos_theme.lib.mailer import Message, Mail
from pylons import config

import logging

log = logging.getLogger(__name__)


def send_feedback(context):
    '''
    Sends a feedback message to the recipients in the feedback.recipients
    config list.

    :param dict context: A dictionary containing the name, email and feedback
                         from a user.
    '''

    body = render_jinja2('emails/feedback.txt', context)
    subject = 'IOOS Catalog Feedback'

    recipients = config.get('feedback.recipients')
    if not recipients:
        log.info("No recipients specified, feedback email not sent")
        return
    recipients = recipients.split(' ')
    mail = Mail()
    msg = Message(subject, sender=config.get('smtp.mail_from'), recipients=recipients)
    msg.extra_headers = {"referring_site": context['referrer']}
    msg.body = body
    mail.send(msg)
