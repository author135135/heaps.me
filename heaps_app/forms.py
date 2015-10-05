from django import forms
from ckeditor.widgets import CKEditorWidget
from heaps_app import models
from heaps_app.fields import SocialNetworkField


# Front forms

# Search form
class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search'}))


# Filter form
class FilterForm(forms.Form):
    filter_tags = forms.MultipleChoiceField(choices=models.Filter.objects.values_list('pk', 'title'),
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
class CelebrityAdminForm(forms.ModelForm):
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'cols': 116, 'rows': 10}), required=False)
    description = forms.CharField(widget=CKEditorWidget())
