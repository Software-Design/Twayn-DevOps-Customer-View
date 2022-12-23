from django.core.mail import EmailMessage, send_mail
from django.conf import settings

def sendingEmail(recipient,msgtext,subject):
    """
    Send E-Mail after new issue is saved. 
    """
    email_from = settings.EMAIL_FROM
    email = EmailMessage(subject,msgtext,email_from,recipient)
    email.send()
