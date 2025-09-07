from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

alphanumeric = RegexValidator(
    r"^[0-9a-zA-Z]*$", "Only alphanumeric characters are allowed."
)


def validate_decimals(value):
    try:
        return round(float(value), 2)
    except Exception:
        raise ValidationError(
            _("%(value)s is not an integer or a float  number"),
            params={"value": value},
        )


def validate_capitalized(value):
    if value != value.capitalize():
        raise ValidationError(
            "Invalid (not capitalized) value: %(value)s",
            code="invalid",
            params={"value": value},
        )
