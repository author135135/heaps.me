from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from ckeditor.widgets import CKEditorWidget
from heaps_app import models
from heaps_app.fields import SocialNetworkField, CroppedImageField
from heaps_app.widgets import MultiTextInput
from django.utils.translation import ugettext_lazy as _


# Front forms
class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Search'), 'class': 'search'}))


class CelebrityAddForm(forms.ModelForm):
    photo = forms.ImageField(required=False, show_hidden_initial=True, initial='defaults/default-pers-no-photo.png')
    social_network = SocialNetworkField(widget=MultiTextInput(attrs={'placeholder': _('Place for link')}))

    class Meta:
        model = models.Celebrity
        fields = ('firstname', 'lastname', 'nickname', 'description')
        labels = {
            'firstname': _('Firstname'),
            'lastname': _('Lastname'),
            'nickname': _('Nickname'),
            'description': _('Short description'),
        }

    def clean(self):
        cleaned_data = super(CelebrityAddForm, self).clean()
        firstname = cleaned_data['firstname']
        lastname = cleaned_data['lastname']
        nickname = cleaned_data['nickname']

        if not any([firstname, lastname, nickname]):
            self.add_error('firstname', _('One of this field must contain some value'))
            self.add_error('lastname', _('One of this field must contain some value'))
            self.add_error('nickname', _('One of this field must contain some value'))

    def save(self, commit=True):
        celebrity = super(CelebrityAddForm, self).save(commit)

        for social_url in self.cleaned_data['social_network']:
            social_network = celebrity.socialnetwork_set.create(url=social_url)

            if social_network.detect_social_by_url():
                social_network.save()

        upload_photo = self.cleaned_data['photo']

        if upload_photo:
            photo = celebrity.photo_set.create(image=upload_photo)
            photo.save()


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': _('Email'), 'id': 'login-email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': _('Password'),
                                                                 'id': 'login-password'}))


class RegistrationForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': _('Email'), 'id': 'registration-email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': _('Password'),
                                                                 'id': 'registration-password'}))
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': _('Password repeat')}))

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            return email

        raise forms.ValidationError(_('E-mail address is already taken'), code='invalid')

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password != password_repeat:
            self.add_error('password_repeat', _('Password and Password repeat not equal'))


class EmailVerificationForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': _('Email'), 'id': 'verification-email'}))


class PasswordForgottenForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': _('Email'), 'id': 'forgotten-email'}))

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            raise forms.ValidationError(_('E-mail address not found'), code='invalid')

        return email


class AccountSettingsForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput, required=False)
    password_repeat = forms.CharField(label=_('Password repeat'), widget=forms.PasswordInput, required=False)
    avatar = CroppedImageField(required=False)

    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': _('Firstname'),
            'last_name': _('Lastname'),
        }

    def clean(self):
        cleaned_data = super(AccountSettingsForm, self).clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if (password or password_repeat) and password != password_repeat:
            self.add_error('password_repeat', _('Password and Password repeat not equal'))

    def save(self, commit=True):
        user = super(AccountSettingsForm, self).save(commit=False)
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('password_repeat')

        if password and password_repeat:
            user.set_password(password)

        avatar = self.cleaned_data['avatar']

        print avatar

        if avatar:
            user.avatar = avatar

        if commit:
            user.save()

        return user


# Admin forms
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password repeat'), widget=forms.PasswordInput)

    class Meta:
        model = models.User
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if (password1 and password2) and password1 != password2:
            raise forms.ValidationError(_('Password and Password repeat not equal'), code='invalid')
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(required=False)

    class Meta:
        model = models.User
        fields = ('email',)

    def clean_password(self):
        return self.initial['password']


class CelebrityAdminForm(forms.ModelForm):
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'cols': 116, 'rows': 10}), required=False)

    class Meta:
        widgets = {
            'description': CKEditorWidget(),
            'filter': forms.SelectMultiple(attrs={'size': 15})
        }
