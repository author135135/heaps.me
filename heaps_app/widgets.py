from django.forms.utils import flatatt
from django.forms.widgets import TextInput, FileInput
from django.utils.datastructures import MergeDict, MultiValueDict
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class MultiTextInput(TextInput):
    def render(self, name, value, attrs=None):
        if value is None or not value:
            value = ['']
        attrs.update({'id': ''})
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)

        inputs = list()
        for i, v in enumerate(value):
            input_attrs = dict(value=force_text(v), **final_attrs)
            inputs.append(format_html(u'<input{} />', flatatt(input_attrs)))
        return mark_safe('\n'.join(inputs))

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            list_data = filter(lambda v: v, data.getlist(name))
            if list_data:
                return list_data
        return data.get(name, None)


class CoordinatesImageInput(FileInput):
    def render(self, name, value, attrs=None):
        file_input = super(CoordinatesImageInput, self).render(name, value, attrs)

        inputs = list()
        inputs.append(file_input)

        hidden_fields_attrs = self.build_attrs(type='hidden')

        for i in ['x', 'y', 'w', 'h']:
            input_attrs = dict(
                name='crop_attr_{0}'.format(i),
                id='id_crop_attr_{0}'.format(i),
                **hidden_fields_attrs
            )
            inputs.append(format_html(u'<input{} />', flatatt(input_attrs)))

        return mark_safe('\n'.join(inputs))

    def value_from_datadict(self, data, files, name):
        return dict(
            image=files.get(name),
            crop_attr_x=data.get('crop_attr_x'),
            crop_attr_y=data.get('crop_attr_y'),
            crop_attr_w=data.get('crop_attr_w'),
            crop_attr_h=data.get('crop_attr_h'),
        )
