from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

UserModel = get_user_model()

@shared_task
def send_welcome_email_task(user_id: int) -> None:
    try:
        user = UserModel.objects.get(pk=user_id)
    except UserModel.DoesNotExist:
        return

    if not user.email:
        return

    send_mail(
        subject='Welcome to FictionBuilder',
        message=(
            f'Hello, {user.username}!\n\n'
            'Your account was created successfully. '
            'Welcome to Fictional Universe Builder.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )