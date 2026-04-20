from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.text import slugify


class SetOwnerMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ObjectManagementMixin:
    moderator_group_name = "Moderators"
    def get_permission_object(self):
        if hasattr(self, "object") and self.object is not None:
            return self.object
        return self.get_object()

    def user_can_manage_object(self, obj=None):
        user = self.request.user

        if not user.is_authenticated:
            return False

        obj = obj or self.get_permission_object()
        return (
            user.is_superuser
            or user == obj.owner
            or user.groups.filter(name=self.moderator_group_name).exists()
        )

class CanManageObjectRequiredMixin(ObjectManagementMixin, UserPassesTestMixin):
    raise_exception = True

    def get_object(self, queryset=None):
        if not hasattr(self, '_cached_object'):
            self._cached_object = super().get_object(queryset)
        return self._cached_object

    def test_func(self):
        return self.user_can_manage_object()

class CanManageObjectContextMixin(ObjectManagementMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_object"] = self.user_can_manage_object()
        return context

class UnpublishedAccessMixin:
    moderator_group_name = "Moderators"
    def can_view_unpublished(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name=self.moderator_group_name).exists()
        )



class FilterOwnerFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class UniverseSlugObjectMixin:
    model = None
    slug_url_kwarg = 'slug'
    universe_slug_url_kwarg = 'universe_slug'

    def get_queryset(self):
        return self.model.objects.select_related('universe')

    def get_object(self, qs=None):
        qs = qs or self.get_queryset()

        return get_object_or_404(
            qs,
            slug=self.kwargs[self.slug_url_kwarg],
            universe__slug=self.kwargs[self.universe_slug_url_kwarg],
        )


class MessageCreateUpdateViewMixin:
    success_message_action = 'saved'

    def form_valid(self, form):
        response = super().form_valid(form)
        model_name = self.object._meta.verbose_name.title()
        messages.success(self.request, message=f'{model_name} "{self.object}" was {self.success_message_action} successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, message='Please correct the errors below.')
        return super().form_invalid(form)


class ConfirmDeleteViewMixin:
    def form_valid(self, form):
        name = str(self.object)
        model_name = self.object._meta.verbose_name.title()
        messages.success(self.request, message=f'{model_name} "{name}" was deleted successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, message='Please review the form before deleting.')
        return super().form_invalid(form)



# Forms
class OwnerScopedFormMixin:
    user = None

    def style_form_fields(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def is_moderator(self):
        return self.user is not None and self.user.groups.filter(name='Moderators').exists()

    def get_owner_for_queryset(self):
        user = self.user
        if not user or not user.is_authenticated:
            return None

        if self.instance.pk and (user.is_superuser or self.is_moderator()):
            return self.instance.owner
        return user

    def get_selected_universe_id(self):
        universe_raw = self.data.get('universe')
        if self.instance.pk:
            try:
                return int(universe_raw)
            except (ValueError, TypeError):
                return self.instance.universe_id
        if universe_raw:
            try:
                return int(universe_raw)
            except (ValueError, TypeError):
                return None
        return None


# Models.
class SlugMixin:
    slug_field_name = 'slug'
    slug_source_field = None
    slug_related_field = 'universe'
    slug_dependency_fields = None

    def get_slug_source_value(self):
        return getattr(self, self.slug_source_field)
    def get_slug_related_value(self):
        return getattr(self, self.slug_related_field)
    def get_slug_related_id(self):
        return getattr(self, f"{self.slug_related_field}_id")
    def get_slug_dependency_fields(self):
        if self.slug_dependency_fields is not None:
            return self.slug_dependency_fields
        return (self.slug_source_field,)



    def save(self, *args, **kwargs):
        base_slug = slugify(self.get_slug_source_value())

        if not base_slug:
            raise ValidationError({
                self.slug_source_field: "This field must contain at least one letter or number"
            })

        if not self.pk:
            slug = base_slug
        else:
            dependency_fields = self.get_slug_dependency_fields()
            old_instance = type(self).objects.only(
                *dependency_fields,
                f"{self.slug_related_field}_id",
                # self.slug_source_field, self.slug_related_field
            ).get(pk=self.pk)

            source_changed = any(getattr(old_instance, field) != getattr(self, field) for field in dependency_fields)
            related_changed = getattr(old_instance, f"{self.slug_related_field}_id") != self.get_slug_related_id()

            if source_changed or related_changed:
                slug = base_slug
            else:
                slug = getattr(self, self.slug_field_name) or base_slug


        final_slug = slug
        counter = 1

        while type(self).objects.filter(
                **{
                    self.slug_field_name: final_slug,
                    f"{self.slug_related_field}_id": self.get_slug_related_id()
                }
        ).exclude(pk=self.pk).exists():
            final_slug = f"{slug}-{counter}"
            counter += 1

        setattr(self, self.slug_field_name, final_slug)

        super().save(*args, **kwargs)


