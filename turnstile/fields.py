import inspect

from django import forms
from django.utils.translation import gettext_lazy as _

from turnstile.services import TurnstileService, TurnstileVerificationException
from turnstile.settings import DEFAULT_CONFIG, ENABLE
from turnstile.widgets import TurnstileWidget


class TurnstileField(forms.Field):
    widget = TurnstileWidget
    default_error_messages = {
        'error_turnstile': _('Turnstile could not be verified.'),
        'invalid_turnstile': _('Turnstile could not be verified.'),
        'required': _('Please prove you are a human.'),
    }

    def __init__(self, remote_ip = None, **kwargs):
        self.remote_ip = remote_ip
        superclass_parameters = inspect.signature(super().__init__).parameters
        superclass_kwargs = {}
        widget_settings = DEFAULT_CONFIG.copy()
        for key, value in kwargs.items():
            if key in superclass_parameters:
                superclass_kwargs[key] = value
            else:
                widget_settings[key] = value

        widget_url_settings = {}
        for prop in filter(lambda p: p in widget_settings, ('onload', 'render', 'hl')):
            widget_url_settings[prop] = widget_settings[prop]
            del widget_settings[prop]
        self.widget_settings = widget_settings

        super().__init__(**superclass_kwargs)

        self.widget.extra_url = widget_url_settings

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        for key, value in self.widget_settings.items():
            attrs['data-%s' % key] = value
        return attrs

    def validate(self, value):
        if not ENABLE:
            return
        super().validate(value)

        service = TurnstileService()

        try:
            result = service.verify(
                value,
                self.remote_ip
            )

        except TurnstileVerificationException:
            raise forms.ValidationError(self.error_messages['error_turnstile'],code='error_turnstile')

        if not result.success:
            raise forms.ValidationError(self.error_messages['invalid_turnstile'], code='invalid_turnstile')
