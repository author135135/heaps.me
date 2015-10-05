from django.forms import CharField, ValidationError
from django.core.validators import URLValidator
from heaps_app.widgets import MultiTextField


class SocialNetworkField(CharField):
    widget = MultiTextField

    def to_python(self, value):
        if value:
            return value

        raise ValidationError("This field is required", code="invalid")

    def validate(self, value):
        url_validator = URLValidator()

        for url_address in value:
            url_validator(url_address)
