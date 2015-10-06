from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model
from ckeditor.widgets import CKEditorWidget
from heaps_app import models
from heaps_app.fields import SocialNetworkField


# Front forms

# Search form
class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search'}))


# Filter form
# FILTER_CHOICES = models.Filter.objects.values_list('pk', 'title')


class FilterForm(forms.Form):
    filter_tags = forms.MultipleChoiceField(choices=[],
                                            widget=forms.CheckboxSelectMultiple())


# Add celebrity form
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
            raise forms.ValidationError("One of `firstname`, `lastname` or `nickname` must contain some value",
                                        code='invalid')

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


# Admin forms
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password repeat', widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Password and Password repeat not equal')
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ('email',)


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(required=False)

    def clean_password(self):
        return self.initial['password']

    class Meta:
        model = get_user_model()
        fields = ['email', ]


class CelebrityAdminForm(forms.ModelForm):
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'cols': 116, 'rows': 10}), required=False)
    description = forms.CharField(widget=CKEditorWidget())
