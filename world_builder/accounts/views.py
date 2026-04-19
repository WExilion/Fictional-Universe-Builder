from django.contrib import messages
from django.contrib.auth import get_user_model, logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, DetailView, DeleteView

from accounts.forms import UserRegisterForm, ProfileForm, UserDeleteForm, UserUpdateForm, UserLoginForm, \
    CustomPasswordChangeForm
from accounts.models import Profile
from accounts.tasks import send_welcome_email_task
from common.mixins import ConfirmDeleteViewMixin
from universes.models import Universe

UserModel = get_user_model()

# Create your views here.
class UserRegisterView(CreateView):
    model = UserModel
    form_class = UserRegisterForm
    template_name = 'accounts/user-register.html'
    success_url = reverse_lazy('common:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('common:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            login(
                self.request,
                self.object,
                backend='django.contrib.auth.backends.ModelBackend',
            )
            # user = self.object
            transaction.on_commit(
                lambda: send_welcome_email_task.delay(self.object.pk)
            )
        return response

class UserLoginView(LoginView):
    template_name = 'accounts/user-login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('common:home')

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile-detail.html'
    context_object_name = 'profile'

    def get_object(self): # noqa
        return get_object_or_404(Profile, owner__pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewed_user = self.object.owner
        context['is_owner'] = self.request.user == viewed_user
        context['universes'] = Universe.objects.filter(owner=viewed_user)
        # context['characters'] = Character.objects.filter(owner=viewed_user)
        # context['locations'] = Location.objects.filter(owner=viewed_user)
        # context['stories'] = Story.objects.filter(owner=viewed_user)
        return context

class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'accounts/profile-edit.html'

    def get_object(self):  # noqa
        return self.request.user.profile # noqa
        # return get_object_or_404(Profile, owner=self.request.user)

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=self.get_object())
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=self.get_object())

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect(reverse('accounts:detail', kwargs={'pk': request.user.pk}))

        messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
        })


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password-change.html'
    success_url = reverse_lazy('accounts:password-change-done')

class UserDeleteView(LoginRequiredMixin, ConfirmDeleteViewMixin, DeleteView):
    model = UserModel
    form_class = UserDeleteForm
    template_name = 'accounts/user-delete.html'
    success_url = reverse_lazy('common:home')

    def get_object(self): # noqa
        return get_object_or_404(UserModel, pk=self.request.user.pk)

    def form_valid(self, form):
        self.object = self.get_object()
        logout(self.request)
        return super().form_valid(form)




