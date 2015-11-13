from StringIO import StringIO
from PIL import Image
from django.forms import CharField, ImageField, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.validators import URLValidator
from heaps_app.widgets import MultiTextInput, CoordinatesImageInput
from django.utils.translation import ugettext_lazy as _


class SocialNetworkField(CharField):
    widget = MultiTextInput

    def to_python(self, value):
        if value:
            return value

        raise ValidationError(_('This field is required'), code="invalid")

    def validate(self, value):
        url_validator = URLValidator()

        for url_address in value:
            url_validator(url_address)


class CroppedImageField(ImageField):
    widget = CoordinatesImageInput

    def to_python(self, data):
        image_file = super(CroppedImageField, self).to_python(data['image'])

        if image_file:
            crop_attr_x = data['crop_attr_x']
            crop_attr_y = data['crop_attr_y']
            crop_attr_w = data['crop_attr_w']
            crop_attr_h = data['crop_attr_h']

            if any([crop_attr_x, crop_attr_y, crop_attr_w, crop_attr_h]):
                crop_attr_x = int(crop_attr_x)
                crop_attr_y = int(crop_attr_y)
                crop_attr_w = int(crop_attr_w)
                crop_attr_h = int(crop_attr_h)

                image = Image.open(StringIO(image_file.read()))

                crop_image = image.crop([
                    crop_attr_x,
                    crop_attr_y,
                    crop_attr_x + crop_attr_w,
                    crop_attr_y + crop_attr_h,
                ])

                new_image = StringIO()
                crop_image.save(new_image, image.format)
                new_image.seek(0)

                image_file = SimpleUploadedFile(image_file.name, new_image.read(), content_type=image_file.content_type)

        return image_file
