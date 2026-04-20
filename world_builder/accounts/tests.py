from unittest.mock import patch

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, get_user
from django.contrib.auth.models import Group

from accounts.forms import CustomPasswordChangeForm, UserRegisterForm, UserLoginForm, ProfileForm
from accounts.models import Profile
from accounts.tasks import send_welcome_email_task
from world_builder.settings import DEFAULT_FROM_EMAIL

UserModel = get_user_model()

# Create your tests here.
class UserManagerTests(TestCase):

    def test_create_user_sets_email_username_and_default_flags(self):
        user = UserModel.objects.create_user(
            email='USER@Test.com',
            username='user',
            password='Password123!',
        )
        self.assertEqual(user.email, 'USER@test.com')
        self.assertEqual(user.username, 'user')
        self.assertTrue(user.check_password('Password123!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_sets_staff_and_superuser_flags(self):
        user = UserModel.objects.create_superuser(
            email='admin@test.com',
            username='admin',
            password='Password123!',
        )
        self.assertEqual(user.email, 'admin@test.com')
        self.assertEqual(user.username, 'admin')
        self.assertTrue(user.check_password('Password123!'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaisesMessage(ValueError, 'Email is required'):
            UserModel.objects.create_user(email=None, username='user', password='Password123!')

    def test_create_user_without_username_raises_error(self):
        with self.assertRaisesMessage(ValueError, 'Username is required'):
            UserModel.objects.create_user(email='user@test.com', username=None, password='Password123!')

    def test_create_superuser_with_is_staff_false_raises_error(self):
        with self.assertRaisesMessage(ValueError, 'Superuser must have is_staff=True.'):
            UserModel.objects.create_superuser(
                email='admin@test.com',
                username='admin',
                password='Password123!',
                is_staff=False,
            )
    def test_create_superuser_with_is_superuser_false_raises_error(self):
        with self.assertRaisesMessage(ValueError, 'Superuser must have is_superuser=True.'):
            UserModel.objects.create_superuser(
                email='admin@test.com',
                username='admin',
                password='Password123!',
                is_superuser=False,
            )



class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='profile@test.com',
            username='profileuser',
            password='Password123!'
        )

    def test_profile_str_returns_profile_of_username(self):
        self.assertEqual(str(self.user.profile), 'Profile of profileuser')

    def test_profile_full_name_returns_first_and_last_name(self):
        profile = self.user.profile
        profile.first_name = 'John'
        profile.last_name = 'Doe'
        profile.save()

        self.assertEqual(profile.full_name, 'John Doe')

    def test_profile_full_name_returns_empty_string_without_names(self):
        profile = self.user.profile
        profile.first_name = ''
        profile.last_name = ''
        profile.save()

        self.assertEqual(profile.full_name, '')

    def test_profile_is_created_for_new_user(self):
        self.assertTrue(Profile.objects.filter(owner=self.user).exists())


class UserSignalTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='signal@test.com',
            username='signaluser',
            password='StrongPass123!',
        )

    def test_user_creation_creates_profile(self):
        self.assertTrue(Profile.objects.filter(owner=self.user).exists())

    def test_user_creation_adds_user_to_members_group(self):
        self.assertTrue(self.user.groups.filter(name='Members').exists())


class GroupPermissionSignalTests(TestCase):
    def test_members_group_exists_after_migrations(self):
        self.assertTrue(Group.objects.filter(name='Members').exists())

    def test_moderators_group_exists_after_migrations(self):
        self.assertTrue(Group.objects.filter(name='Moderators').exists())

    def test_members_group_has_add_and_view_story_permissions(self):
        group = Group.objects.get(name='Members')

        self.assertTrue(group.permissions.filter(codename='view_story').exists())
        self.assertTrue(group.permissions.filter(codename='add_story').exists())
        self.assertFalse(group.permissions.filter(codename='delete_story').exists())

    def test_moderators_group_has_full_story_permissions(self):
        group = Group.objects.get(name='Moderators')

        self.assertTrue(group.permissions.filter(codename='view_story').exists())
        self.assertTrue(group.permissions.filter(codename='add_story').exists())
        self.assertTrue(group.permissions.filter(codename='change_story').exists())
        self.assertTrue(group.permissions.filter(codename='delete_story').exists())



class UserRegisterFormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'email': 'test@example.com',
            'username': 'tester123',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    def test_form_sets_email_and_username_field_configuration(self):
        form = UserRegisterForm()

        self.assertEqual(form.fields['email'].label, 'Email Address')
        self.assertEqual(form.fields['username'].label, 'Username')
        self.assertEqual(form.fields['email'].help_text, 'Used for login. We value your privacy.')
        self.assertEqual(form.fields['username'].help_text, 'Visible to others on your creations.')
        self.assertIn('form-control', form.fields['email'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['username'].widget.attrs['class'])

    def test_form_sets_custom_password_labels_and_widgets(self):
        form = UserRegisterForm()
        self.assertEqual(form.fields['password1'].label, 'Password')
        self.assertEqual(form.fields['password2'].label, 'Confirm Password')
        self.assertIn('form-control', form.fields['password1'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['password2'].widget.attrs['class'])

    def test_form_with_invalid_email_shows_error(self):
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'

        form = UserRegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Enter a valid email address.'])

    def test_form_with_duplicate_email_shows_error(self):
        UserModel.objects.create_user(
            email=self.valid_data['email'],
            username='existinguser',
            password='Password123!',
        )

        data = self.valid_data.copy()

        form = UserRegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['This email is already in use. Try logging in?'])

    def test_form_with_duplicate_username_shows_error(self):
        UserModel.objects.create_user(
            email='existing@example.com',
            username=self.valid_data['username'],
            password='Password123!',
        )

        data = self.valid_data.copy()

        form = UserRegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This username is taken. Try another?'])

    def test_form_with_blank_email_shows_required_error(self):
        data = self.valid_data.copy()
        data['email'] = ''

        form = UserRegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Enter an email address.'])

    def test_form_with_blank_username_shows_required_error(self):
        data = self.valid_data.copy()
        data['username'] = ''

        form = UserRegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Enter a username.'])


    def test_form_with_blank_password1_shows_required_error(self):
        data = self.valid_data.copy()
        data['password1'] = ''

        form = UserRegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password1'], ['Enter a password.'])

    def test_form_with_blank_password2_shows_required_error(self):
        data = self.valid_data.copy()
        data['password2'] = ''

        form = UserRegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ['Confirm your password.'])


class UserLoginFormTests(TestCase):
    def test_form_sets_custom_labels_and_widgets(self):
        form = UserLoginForm()

        self.assertEqual(form.fields['username'].label, 'Email Address')
        self.assertEqual(form.fields['password'].label, 'Password')
        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], 'e.g., writer@example.com')
        self.assertIn('form-control', form.fields['username'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['password'].widget.attrs['class'])

    def test_form_with_blank_username_shows_required_error(self):
        form = UserLoginForm(data={
            'username': '',
            'password': 'StrongPass123!',
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Email address is required.'])

    def test_form_with_blank_password_shows_required_error(self):
        form = UserLoginForm(data={
            'username': 'test@example.com',
            'password': '',
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['Password is required.'])


class ProfileFormTests(TestCase):
    def test_all_fields_have_form_control_class(self):
        form = ProfileForm()

        expected_fields = [
            'avatar',
            'first_name',
            'last_name',
            'date_of_birth',
            'location',
            'gender',
            'description',
        ]

        for field_name in expected_fields:
            self.assertIn('form-control', form.fields[field_name].widget.attrs.get('class', ''))

    def test_form_with_too_long_first_name_shows_max_length_error(self):
        form = ProfileForm(data={
            'first_name': 'a' * 51,
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['first_name'],
            ['First name cannot exceed 50 characters.']
        )

    def test_form_with_too_long_last_name_shows_max_length_error(self):
        form = ProfileForm(data={
            'last_name': 'a' * 51,
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['last_name'],
            ['Last name cannot exceed 50 characters.']
        )

    def test_form_with_too_long_location_shows_max_length_error(self):
        form = ProfileForm(data={
            'location': 'a' * 51,
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['location'],
            ['Location cannot exceed 50 characters.']
        )



class UserRegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse('accounts:register')
        self.valid_data = {
            'email': 'test@example.com',
            'username': 'tester123',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    @patch('accounts.views.send_welcome_email_task.delay')
    def test_register_with_valid_data_queues_welcome_email_task(self, mock_delay):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, reverse('common:home'))
        user = UserModel.objects.get(email=self.valid_data['email'])
        mock_delay.assert_called_once_with(user.pk)


    @patch('accounts.views.send_welcome_email_task.delay')
    def test_register_with_invalid_data_does_not_queue_welcome_email_task(self, mock_delay):
        invalid_data = self.valid_data.copy()
        invalid_data['password2'] = 'WrongPass123!'

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserModel.objects.filter(email=self.valid_data['email']).exists())
        mock_delay.assert_not_called()


    def test_register_with_valid_data_logs_in_user(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, reverse('common:home'))
        user = UserModel.objects.get(email=self.valid_data['email'])
        self.assertEqual(get_user(self.client).pk, user.pk)


    def test_authenticated_user_is_redirected_from_register_page(self):
        user = UserModel.objects.create_user(
            email='logged@test.com',
            username='loggeduser',
            password='StrongPass123!',
        )
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('common:home'))


class UserLoginViewTests(TestCase):
    def setUp(self):
        self.url = reverse('accounts:login')
        self.user = UserModel.objects.create_user(
            email='test@example.com',
            username='tester123',
            password='StrongPass123!',
        )
        self.valid_data = {
            'username': 'test@example.com',
            'password': 'StrongPass123!',
        }

    def test_login_with_valid_credentials(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, reverse('common:home'))
        self.assertEqual(get_user(self.client).pk, self.user.pk)
        # self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_with_invalid_credentials(self):
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'WrongPass123!'
        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user(self.client).is_authenticated)
        # self.assertIsNone(get_user(self.client).pk)
        # self.assertNotIn('_auth_user_id', self.client.session)

    def test_authenticated_user_is_redirected_from_login_page(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('common:home'))




class ProfileDetailViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='owner@test.com',
            username='owneruser',
            password='Password123!',
        )
        self.other_user = UserModel.objects.create_user(
            email='other@test.com',
            username='otheruser',
            password='Password123!',
        )
        self.url = reverse('accounts:detail', kwargs={'pk': self.user.pk})

    def test_profile_detail_accessible_to_logged_in_user(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile-detail.html')

    def test_profile_detail_redirects_anonymous_user(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")

    def test_profile_detail_sets_is_owner_true_for_profile_owner(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertTrue(response.context['is_owner'])

    def test_profile_detail_sets_is_owner_false_for_non_owner(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.url)

        self.assertFalse(response.context['is_owner'])



class ProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='update@test.com',
            username='updateuser',
            password='Password123!',
        )
        self.url = reverse('accounts:edit')
        self.client.force_login(self.user)
        self.valid_data = {
            'email': 'newemail@test.com',
            'username': 'newusername',
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'Male',
        }

    def test_profile_update_get_includes_user_and_profile_forms(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)
        self.assertTemplateUsed(response, 'accounts/profile-edit.html')

    def test_profile_update_with_current_email_and_username_succeeds(self):
        data = {
            'email': 'update@test.com',
            'username': 'updateuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'Male',
        }

        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.user.pk}))

    def test_profile_update_with_new_email_and_username_succeeds(self):
        response = self.client.post(self.url, self.valid_data)

        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()

        self.assertRedirects(response, reverse('accounts:detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(self.user.email, 'newemail@test.com')
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.profile.first_name, 'John')

    def test_profile_update_redirects_anonymous_user(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")


    def test_profile_update_with_invalid_email_shows_error(self):
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['user_form'].errors)

    def test_profile_update_with_duplicate_email_shows_error(self):
        UserModel.objects.create_user(
            email='other@test.com',
            username='otheruser',
            password='Password123!'
        )
        data = self.valid_data.copy()
        data['email'] = 'other@test.com'

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['user_form'].errors)

    def test_profile_update_with_duplicate_username_shows_error(self):
        UserModel.objects.create_user(
            email='other@test.com',
            username='otheruser',
            password='Password123!'
        )
        data = self.valid_data.copy()
        data['username'] = 'otheruser'

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['user_form'].errors)


    def test_profile_update_with_blank_email_shows_required_error(self):
        data = self.valid_data.copy()
        data['email'] = ''

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['user_form'].errors)

    def test_profile_update_with_blank_username_shows_required_error(self):
        data = self.valid_data.copy()
        data['username'] = ''

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['user_form'].errors)



class CustomPasswordChangeViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='password@test.com',
            username='passworduser',
            password='OldPassword123!',
        )
        self.url = reverse('accounts:password-change')
        self.client.force_login(self.user)
        self.valid_data = {
            'old_password': 'OldPassword123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!',
        }

    def test_password_change_get_uses_custom_form_and_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password-change.html')
        self.assertIsInstance(response.context['form'], CustomPasswordChangeForm)


    def test_password_change_with_valid_data_updates_password(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, reverse('accounts:password-change-done'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_password_change_with_wrong_old_password_shows_error(self):
        data = self.valid_data.copy()
        data['old_password'] = 'WrongOldPassword123!'

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('old_password', response.context['form'].errors)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPassword123!'))

    def test_password_change_with_mismatched_new_passwords_shows_error(self):
        data = self.valid_data.copy()
        data['new_password2'] = 'DifferentNewPassword123!'

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('new_password2', response.context['form'].errors)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPassword123!'))

    def test_password_change_redirects_anonymous_user(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")



class UserDeleteViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='delete@example.com',
            username='deleteuser',
            password='Password123!',
        )
        self.url = reverse('accounts:delete')
        self.client.force_login(self.user)

    def test_user_delete_post_removes_user(self):
        response = self.client.post(self.url, {'confirm': 'yes'})

        self.assertRedirects(response, reverse('common:home'))
        self.assertFalse(UserModel.objects.filter(pk=self.user.pk).exists())
        self.assertNotIn('_auth_user_id', self.client.session)


    def test_user_delete_get_loads_confirmation_page(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user-delete.html')
        self.assertIn('form', response.context)

    def test_user_delete_without_confirmation_does_not_delete_user(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserModel.objects.filter(pk=self.user.pk).exists())
        self.assertFormError(
            response.context['form'],
            'confirm',
            'You must confirm before deleting your account.'
        )

    def test_user_delete_redirects_anonymous_user(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")



class WelcomeEmailTaskTests(TestCase):
    def test_send_welcome_email_task_sends_email(self):
        user = UserModel.objects.create_user(
            email='task@test.com',
            username='taskuser',
            password='Password123!'
        )

        send_welcome_email_task(user.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, DEFAULT_FROM_EMAIL)
        self.assertEqual(mail.outbox[0].subject, 'Welcome to FictionBuilder')
        self.assertIn('taskuser', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['task@test.com'])


