from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from turnstile import settings
from turnstile.services import TurnstileService, TurnstileVerificationException

try:
    from rest_framework.exceptions import ValidationError, APIException
except ImportError as exc:
    raise ImproperlyConfigured('Turnstile DRF mixin requires Django REST Framework.') from exc


class TurnstileValidationMixin:

    captcha_field_name = 'cf-turnstile-response'
    methods = ["POST"]

    def initial(self, request, *args, **kwargs):
        """
        Overrides the initial method to include Turnstile validation for 
        specified HTTP methods.
        """
        super().initial(request, *args, **kwargs)

        if request.method not in self.methods:
            return
        if not self.should_validate_turnstile():
            return

        self.validate_turnstile(request)

    def should_validate_turnstile(self):
        """
        Turnstile validation is automatically skipped when using default test keys.
        """
        sitekey = getattr(settings, 'SITEKEY')
        secret = getattr(settings, 'SECRET')

        return not (
            sitekey == settings.TEST_SITEKEY and
            secret == settings.TEST_SECRET
        )

    def get_captcha_token(self, request):
        """
        Retrieves the captcha token from the request data.
        """
        return request.data.get(self.captcha_field_name)

    def validate_turnstile(self, request):
        """
        Validates the Turnstile token from the request.
        """
        token = self.get_captcha_token(request)

        if not token:
            raise ValidationError({self.captcha_field_name: _('Captcha is required.')})

        if not isinstance(token, str) or len(token) > 2048:
            raise ValidationError({self.captcha_field_name: _('Invalid captcha format.')})

        service = TurnstileService()

        try:
            result = service.verify(
                token,
                request.META.get('REMOTE_ADDR')
            )
        except TurnstileVerificationException as e:
            raise APIException(_('Validation error.')) from e

        if not result.success:
            raise ValidationError({self.captcha_field_name: _('Invalid captcha, captcha has expired or has already been used. Please try again.')})