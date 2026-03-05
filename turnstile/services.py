import json
import socket
from urllib.parse import urlencode
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import URLError, HTTPError
from django.utils.translation import gettext_lazy as _
from dataclasses import dataclass
from typing import List, Optional

from turnstile.settings import SECRET, TIMEOUT, PROXIES, VERIFY_URL, EXPECTED_HOSTNAMES

@dataclass
class TurnstileVerificationResult:
    """        
    A dataclass representing the result of a Turnstile verification.
    - success: A boolean indicating whether the verification was successful.
    - error_codes: A list of error codes returned by the Turnstile API, if any.
    - hostname: The hostname of the site where the verification was performed, if available.
    """
    success: bool
    error_codes: List[str]
    hostname: Optional[str]

class TurnstileVerificationException(Exception):
    """
    Custom exception for Turnstile verification errors.
    """
    pass

class TurnstileService:
    def verify(self, token, remote_ip=None):
        """
        Verifies a Turnstile token.
        """
        data = {
            'secret': SECRET,
            'response': token,
        }

        if remote_ip:
            data['remoteip'] = remote_ip

        encoded_data = urlencode(data).encode()
        request = Request(VERIFY_URL, encoded_data)
        opener = build_opener(ProxyHandler(PROXIES))

        try:
            response = opener.open(request, timeout=TIMEOUT)
            body = json.loads(response.read().decode())

        except (HTTPError, URLError, socket.timeout) as e:
            error_codes = []
            if isinstance(e, HTTPError):
                try:
                    body = json.loads(e.read().decode())
                    error_codes = body.get('error-codes', [])
                except Exception:
                    pass
            
            raise TurnstileVerificationException('Turnstile exception %s | codes: %s' % (str(e), str(error_codes)))

        success = body.get('success', False)
        error_codes = body.get('error-codes', [])
        hostname = body.get('hostname', None)

        if success and EXPECTED_HOSTNAMES and hostname not in EXPECTED_HOSTNAMES:
            raise TurnstileVerificationException('Invalid hostname: %s' % hostname)

        return TurnstileVerificationResult(success=success, error_codes=error_codes, hostname=hostname)