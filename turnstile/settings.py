from django.conf import settings

JS_API_URL = getattr(settings, 'TURNSTILE_JS_API_URL', 'https://challenges.cloudflare.com/turnstile/v0/api.js')
VERIFY_URL = getattr(settings, 'TURNSTILE_VERIFY_URL', 'https://challenges.cloudflare.com/turnstile/v0/siteverify')
SITEKEY = getattr(settings, 'TURNSTILE_SITEKEY', '1x00000000000000000000AA')
SECRET = getattr(settings, 'TURNSTILE_SECRET', '1x0000000000000000000000000000000AA')
TIMEOUT = getattr(settings, 'TURNSTILE_TIMEOUT', 5)
DEFAULT_CONFIG = getattr(settings, 'TURNSTILE_DEFAULT_CONFIG', {})
PROXIES = getattr(settings, 'TURNSTILE_PROXIES', {})
ENABLE = getattr(settings, 'TURNSTILE_ENABLE', True)
