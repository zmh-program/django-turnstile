================
Django Turnstile
================

Add Cloudflare Turnstile validator widget to the forms of your django project.

This project refers to github project django-hcaptcha (author: AndrejZbin)

Configuration
-------------

Add "turnstile" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'turnstile',
    ]

For development purposes no further configuration is required. By default, django-Turnstile will use dummy keys.

For production, you'll need to obtain your Turnstile site key and secret key and add them to you settings::

    TURNSTILE_SITEKEY = '<your sitekey>'
    TURNSTILE_SECRET = '<your secret key>'


You can also configure your Turnstile widget globally (`see all options <https://developers.cloudflare.com/turnstile>`_)::

    TURNSTILE_DEFAULT_CONFIG = {
        'onload': 'name_of_js_function',
        'render': 'explicit',
        'theme': 'dark',  # do not use data- prefix
        'size': 'compact',  # do not use data- prefix
        ...
    }

If you need to, you can also override default turnstile endpoints::


    TURNSTILE_JS_API_URL = 'https://challenges.cloudflare.com/turnstile/v0/api.js'
    TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

Use proxies::

     TURNSTILE_PROXIES = {
        'http': 'http://127.0.0.1:8000',
     }

Change default verification timeout::

    TURNSTILE_TIMEOUT = 5



Usage
-----------

Simply add TurnstileField to your forms::

    from turnstile.fields import TurnstileField

    class Forms(forms.Form):
        ....
        turnstile = TurnstileField()
        ....

In your template, if you need to, you can then use `{{ form.turnstile }}` to access the field. 

You can override default config by passing additional arguments::

    class Forms(forms.Form):
        ....
        turnstile = TurnstileField(theme='dark', size='compact')
        ....


How it Works
------------------

When a form is submitted by a user, Turnstile's JavaScript will send one POST parameter to your backend: `cf-turnstile-response`. It will be received by your app and will be used to complete the `turnstile` form field in your backend code.

When your app receives these two values, the following will happen:
 
 - Your backend will send these values to the Cloudflare Turnstile servers
 - Their servers will indicate whether the values in the fields are correct
 - If so, your `turnstile` form field will validate correctly
 
Unit Tests
--------------
You will need to disable the Turnstile field in your unit tests, since your tests obviously cannot complete the Turnstile successfully. One way to do so might be something like:

.. code-block:: python

    from unittest.mock import MagicMock, patch

    from django.test import TestCase

    @patch("turnstile.fields.TurnstileField.validate", return_value=True)
    class ContactTest(TestCase):
        test_msg = {
            "name": "pandora",
            "message": "xyz",
            "turnstile": "xxx",  # Any truthy value is fine
        }

        def test_something(self, mock: MagicMock) -> None:
            response = self.client.post("/contact/", self.test_msg)
            self.assertEqual(response.status_code, HTTP_302_FOUND)

Remote IP
------------------
In order to improve bot detection, Turnstile accepts an optional parameter remoteip with the the visitor's IP address.
During server-side validation, it's sent to Cloudflare and it's used as bonus/malus during bot index calculation.
Before using it, make sure to verify whether your country requires a notice or disclaimer, since you may be collecting user information.

remote_ip should be passed from view to form to Turnstile field, you can find an example below.
Note that this is an example, in order to get real client IP REMOTE_ADDR may not be enough.

.. code-block:: python

    # views.py
    def my_view(request):
        remote_ip = request.META.get('REMOTE_ADDR')
        form = MyForm(request.POST or None, remote_ip=remote_ip)

    # forms.py
    class MyForm(forms.Form):
        turnstile = TurnstileField()
    
        def __init__(self, *args, remote_ip=None, **kwargs):
            super().__init__(*args, **kwargs)
            if remote_ip:
                self.fields['turnstile'].remote_ip = remote_ip