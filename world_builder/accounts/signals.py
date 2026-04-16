from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from accounts.models import Profile

UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(owner=instance)


@receiver(post_save, sender=UserModel)
def assign_default_group(sender, instance, created, **kwargs):
    if created:
        members_group, _ = Group.objects.get_or_create(name='Members')
        instance.groups.add(members_group)


# @receiver(post_migrate)
# def create_default_groups(sender, **kwargs):
#     Group.objects.get_or_create(name='Members')
#     Group.objects.get_or_create(name='Moderators')

@receiver(post_migrate)
def setup_groups_and_permissions(sender, **kwargs):
    members_group, _ = Group.objects.get_or_create(name='Members')
    moderators_group, _ = Group.objects.get_or_create(name='Moderators')

    models = [
        ('universes', 'universe'),
        ('universes', 'genre'),
        ('characters', 'character'),
        ('locations', 'location'),
        ('stories', 'story'),
    ]

    for app_label, model_name in models:
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            continue

        permissions = Permission.objects.filter(content_type=content_type)

        moderator_codenames = {
            f'view_{model_name}',
            f'add_{model_name}',
            f'change_{model_name}',
            f'delete_{model_name}',
        }

        member_codenames = {
            f'view_{model_name}',
            f'add_{model_name}',
        }

        moderator_perms = permissions.filter(codename__in=moderator_codenames)
        member_perms = permissions.filter(codename__in=member_codenames)

        moderators_group.permissions.add(*moderator_perms)
        members_group.permissions.add(*member_perms)