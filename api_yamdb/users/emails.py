import uuid

from django.conf import settings
from django.core.mail import send_mail

from users.models import User


def send_confirmation_code_via_email(email):
    subject = 'Ваш код подтверждения'
    confirmation_code = uuid.uuid4()
    message = f'Ваш код подтверждения {confirmation_code}'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    user_obj.confirmation_code = confirmation_code
    user_obj.save()
