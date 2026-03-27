from django.conf import settings

EXPECTED_HOSTNAMES = getattr(settings, 'TURNSTILE_EXPECTED_HOSTNAMES', [])
JS_API_URL = getattr(settings, 'TURNSTILE_JS_API_URL', 'https://challenges.cloudflare.com/turnstile/v0/api.js')
VERIFY_URL = getattr(settings, 'TURNSTILE_VERIFY_URL', 'https://challenges.cloudflare.com/turnstile/v0/siteverify')
TEST_SITEKEY = '1x00000000000000000000AA'
TEST_SECRET = '1x0000000000000000000000000000000AA'
SITEKEY = getattr(settings, 'TURNSTILE_SITEKEY', TEST_SITEKEY)
SECRET = getattr(settings, 'TURNSTILE_SECRET', TEST_SECRET)
TIMEOUT = getattr(settings, 'TURNSTILE_TIMEOUT', 5)
DEFAULT_CONFIG = getattr(settings, 'TURNSTILE_DEFAULT_CONFIG', {})
PROXIES = getattr(settings, 'TURNSTILE_PROXIES', {})
ENABLE = getattr(settings, 'TURNSTILE_ENABLE', True)
