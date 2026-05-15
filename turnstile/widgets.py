from urllib.parse import urlencode
from django import forms
from turnstile.settings import JS_API_URL, SITEKEY, ENABLE, RENDER_SCRIPT


class TurnstileWidget(forms.Widget):
    input_type = "hidden"
    template_name = 'turnstile/forms/widgets/turnstile_widget.html'

    def __init__(self, sitekey=None, render_script=None, *args, **kwargs):
        """
        Initialize the Turnstile widget.
        
        Args:
            sitekey: Optional sitekey to use. If not provided, falls back to
                    settings.TURNSTILE_SITEKEY. Allows multiple Turnstile widgets
                    with different sitekeys on the same page.
            render_script: Optional bool to render Cloudflare API script tag.
                    If not provided, falls back to settings.TURNSTILE_RENDER_SCRIPT.
        """
        self.sitekey = sitekey
        self.render_script = RENDER_SCRIPT if render_script is None else render_script
        self.script_nonce = None
        self.extra_url = {}
        super().__init__(*args, **kwargs)

    @property
    def is_hidden(self):
        return not ENABLE

    def value_from_datadict(self, data, files, name):
        return data.get('cf-turnstile-response')

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        # Use instance sitekey if provided, otherwise fall back to settings
        attrs['data-sitekey'] = self.sitekey or SITEKEY
        return attrs

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['api_url'] = JS_API_URL
        context['render_script'] = self.render_script
        context['script_nonce'] = self.script_nonce
        if self.extra_url:
            context['api_url'] += '?' + urlencode(self.extra_url)
        return context

    def render(self, name, value, attrs=None, renderer=None):
        if not ENABLE:
            return ""
        return super().render(name, value, attrs, renderer)
