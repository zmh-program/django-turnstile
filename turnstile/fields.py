import inspect
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import build_opener, Request, ProxyHandler

from django import forms
from django.utils.translation import gettext_lazy as _

from turnstile.settings import DEFAULT_CONFIG, ENABLE, PROXIES, SECRET, TIMEOUT, VERIFY_URL
from turnstile.widgets import TurnstileWidget


def _resolve_csp_nonce(request):
    if request is None:
        return None

    # Django's CSP nonce may be a LazyNonce that is falsy until stringified.
    # Use an explicit None check so we don't accidentally drop a valid nonce.
    if (nonce := getattr(request, "csp_nonce", None)) is not None:
        return str(nonce)

    try:
        from django.middleware.csp import get_nonce
    except ImportError:
        return None

    try:
        nonce = get_nonce(request)
        # Same here: avoid truthiness checks for LazyNonce.
        if nonce is not None:
            return str(nonce)
    except Exception:
        return None

    return None


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

        widget_runtime_settings = {}
        for prop in filter(lambda p: p in widget_settings, ('sitekey', 'render_script', 'request')):
            widget_runtime_settings[prop] = widget_settings[prop]
            del widget_settings[prop]
        self.widget_settings = widget_settings

        super().__init__(**superclass_kwargs)

        self.widget.extra_url = widget_url_settings
        request = widget_runtime_settings.pop("request", None)
        for key, value in widget_runtime_settings.items():
            setattr(self.widget, key, value)
        if request is not None:
            self.set_request(request)

    def set_request(self, request, override=False):
        if not override and getattr(self.widget, "script_nonce", None):
            return
        resolved_nonce = _resolve_csp_nonce(request)
        if resolved_nonce is not None:
            self.widget.script_nonce = resolved_nonce
        elif override:
            self.widget.script_nonce = None

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        for key, value in self.widget_settings.items():
            attrs[f'data-{key}'] = value
        return attrs

    def validate(self, value):
        if not ENABLE:
            return
        super().validate(value)
        opener = build_opener(ProxyHandler(PROXIES))
        post_data = urlencode({
            'secret': SECRET,
            'response': value,
            'remoteip': self.remote_ip,
        }).encode()
        request = Request(VERIFY_URL, post_data)
        try:
            response = opener.open(request, timeout=TIMEOUT)
        except HTTPError:
            raise forms.ValidationError(self.error_messages['error_turnstile'], code='error_turnstile')

        response_data = json.loads(response.read().decode("utf-8"))

        if not response_data.get('success'):
            raise forms.ValidationError(self.error_messages['invalid_turnstile'], code='invalid_turnstile')
