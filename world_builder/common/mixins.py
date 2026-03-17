from django import forms
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from characters.models import Character
from locations.models import Location


class LocationObjectViewMixin:
    def get_object(self, queryset=None):
        return get_object_or_404(
            Location.objects.select_related(
                'universe',
                'parent_location',
                'parent_location__parent_location',
            ),
            universe__slug=self.kwargs["universe_slug"],
            slug=self.kwargs["slug"],
        )


class CharacterObjectViewMixin:
    def get_object(self, queryset=None):
        return get_object_or_404(
            Character.objects.select_related(
                'universe',
                'location',
                'location__parent_location',
                'location__parent_location__parent_location',
            ),
            universe__slug=self.kwargs["universe_slug"],
            slug=self.kwargs["slug"],
        )

class MessageCreateUpdateViewMixin:
    success_message_action = 'saved'

    def form_valid(self, form):
        response = super().form_valid(form)
        model_name = self.object._meta.verbose_name.title()
        messages.success(self.request, f'{model_name} "{self.object}" was {self.success_message_action} successfully!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ConfirmDeleteViewMixin:
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            name = str(self.object)
            model_name = self.object._meta.verbose_name.title()

            self.object.delete()
            messages.success(request, message=f'{model_name} "{name}" was deleted successfully.')
            return redirect(self.get_success_url())
        else:
            messages.error(request, message='Please review the form before deleting.')
            return self.form_invalid(form)




class NameLengthMixin:
    def _check_name_length(self, field_name: str, min_length: int = 2, field_label: str = None):
        name = self.cleaned_data.get(field_name)
        label = field_label or field_name.replace('_', ' ').title()

        if name and len(name) < min_length:
            raise forms.ValidationError(
                f"{label} must be at least {min_length} characters long."
            )

        return name

