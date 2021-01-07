from flask import current_app, render_template
from flask_mail import Message
from app import mail

def send_email(subject, sender, recipients, html_body, reply_to=None, bcc=None):
    msg = Message(subject, sender=sender, recipients=recipients, reply_to=reply_to, bcc=bcc)
    msg.html = html_body
    mail.send(msg)

def send_contact_email(data):
    send_email(
        subject='Contact Form Inquiry',
        sender='noreply@samplesimp.com',
        recipients=[current_app.config.get('MAIL_ADMIN')],
        reply_to=data.get('email'),
        bcc=data.get('email'),
        html_body=render_template('main/email.html', **data)
    )