from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from ckeditor.widgets import CKEditorWidget
from heaps_app import models
from heaps_app.fields import SocialNetworkField


# Front forms
class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search'}))


class FilterForm(forms.Form):
    FILTER_CHOICES = models.Filter.objects.values_list('pk', 'title')

    filter_tags = forms.MultipleChoiceField(choices=FILTER_CHOICES,
                                            widget=forms.CheckboxSelectMultiple())


class CelebrityForm(forms.ModelForm):
    photo = forms.ImageField(required=False)
    social_network = SocialNetworkField()

    class Meta:
        model = models.Celebrity
        fields = ('firstname', 'lastname', 'nickname', 'description')

    def __init__(self, *args, **kwargs):
        super(CelebrityForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = self.cleaned_data
        firstname = cleaned_data['firstname']
        lastname = cleaned_data['lastname']
        nickname = cleaned_data['nickname']

        if not any([firstname, lastname, nickname]):
            self.add_error('firstname', 'One of this field must contain some value')
            self.add_error('lastname', 'One of this field must contain some value')
            self.add_error('nickname', 'One of this field must contain some value')

    def save(self, commit=True):
        celebrity = super(CelebrityForm, self).save(commit)

        for social_url in self.cleaned_data['social_network']:
            social_network = celebrity.socialnetwork_set.create(url=social_url)

            if social_network.detect_social_by_url():
                social_network.save()

        upload_photo = self.cleaned_data['photo']

        if upload_photo:
            photo = celebrity.photo_set.create(image=upload_photo)
            photo.save()


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class RegistrationForm(LoginForm):
    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            return email

        raise forms.ValidationError("E-mail address is already taken", code='invalid')


class AccountSettingsForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password repeat', widget=forms.PasswordInput, required=False)
    avatar = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(AccountSettingsForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(AccountSettingsForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if ((password1 and password2) and password1 != password2) or (password1 or password2):
            self.add_error('password1', 'Password and Password repeat not equal')
            self.add_error('password2', 'Password and Password repeat not equal')

    def save(self, commit=True):
        user = super(AccountSettingsForm, self).save(commit=False)
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            user.set_password(password1)

        avatar = self.cleaned_data['avatar']

        if avatar:
            user.avatar = avatar

        if commit:
            user.save()
        return user


# Admin forms
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password repeat', widget=forms.PasswordInput)

    class Meta:
        model = models.User
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if (password1 and password2) and password1 != password2:
            raise forms.ValidationError('Password and Password repeat not equal', code='invalid')
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
    description = forms.CharField(widget=CKEditorWidget())
