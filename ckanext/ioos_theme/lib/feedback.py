from ckan.lib.base import render_jinja2
from ckanext.ioos_theme.lib.mailer import Message, Mail
from pylons import config

import logging

log = logging.getLogger(__name__)


def send_feedback(context):

    body = render_jinja2('emails/feedback.txt', context)
    subject = 'IOOS Catalog Feedback'

    recipients = config.get('feedback.recipients')
    if not recipients:
        return

    recipients = recipients.split(' ')
    mail = Mail()
    msg = Message(subject, sender=config.get('smtp.mail_from'), recipients=recipients)
    msg.body = body
    mail.send(msg)
