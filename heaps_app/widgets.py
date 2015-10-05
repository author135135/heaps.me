from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.datastructures import MergeDict, MultiValueDict
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class MultiTextField(TextInput):
    def render(self, name, value, attrs=None):
        if value is None or not value:
            value = ['']
        attrs.update({'id': ''})
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)

        inputs = []
        for i, v in enumerate(value):
            input_attrs = dict(value=force_text(v), **final_attrs)
            inputs.append(format_html('<input{} />', flatatt(input_attrs)))
        return mark_safe('\n'.join(inputs))

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            list_data = filter(lambda v: v, data.getlist(name))
            if list_data:
                return list_data
        return data.get(name, None)
