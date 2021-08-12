import json
import pprint

import checklib
import checklib.utils
import checklib.random
import logging
import requests


# noinspection PyPep8Naming
class default_param:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self, fn):
        def wrapper(*args, **kwargs):
            if isinstance(self.value, dict):
                kwargs[self.name] = checklib.utils.merge_dicts(self.value, kwargs.get(self.name, {}))
            else:
                kwargs[self.name] = kwargs.get(self.name, self.value)
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper


class HttpChecker(checklib.Checker):
    port = 80
    proto = 'http'

    def __init__(self):
        super().__init__()
        self._session = requests.Session()
        self.main_url = ''

    def _check_response(self, response):
        if response.status_code >= 400:
            logging.error("Response is %s" % response.text[:500])
            self.exit(
                checklib.StatusCode.DOWN,
                'Got HTTP status code %d on %s' % (response.status_code, response.url)
            )
        if response.status_code < 200 or response.status_code >= 300:
            self.exit(
                checklib.StatusCode.MUMBLE,
                'Got HTTP status code %d on %s' % (response.status_code, response.url)
            )
        return response

    @default_param('headers', {'User-Agent': checklib.random.useragent()})
    def try_http_get(self, url, *args, **kwargs):
        url = self.get_absolute_url_from_relative(url)
        return self._check_response(self._session.get(url, *args, **kwargs))

    @default_param('headers', {'User-Agent': checklib.random.useragent()})
    def try_http_post(self, url, *args, **kwargs):
        url = self.get_absolute_url_from_relative(url)
        return self._check_response(self._session.post(url, *args, **kwargs))

    def check_page_content(self, response, strings_for_check, failed_message=None):
        message = 'Invalid page content at %url'
        if failed_message is not None:
            message += ': ' + failed_message
        if '%url' in message:
            message = message.replace('%url', response.url)

        for s in strings_for_check:
            self.mumble_if_false(
                s in response.text,
                message,
                'Can\'t find string "%s" in response from %s' % (s, response.url)
            )

        logging.info(
            'Checked %d string(s) on page %s, all of them exist',
            len(strings_for_check),
            response.url
        )

    def get_absolute_url_from_relative(self, url):
        if url.startswith(self.proto):
            return url
        if not url.startswith("/"):
            url = "/" + url
        return self.main_url + url

    def pre_run_command_hook(self, command, arguments):
        super().pre_run_command_hook(command, arguments)
        if command in ('check', 'put', 'get'):
            address = arguments[0]
            self.main_url = '%s://%s:%d' % (self.proto, address, self.port)
            logging.info('Service endpoint is %r' % self.main_url)


class HttpJsonChecker(HttpChecker):
    def try_http_get(self, url, *args, **kwargs):
        response = super().try_http_get(url, *args, **kwargs)
        return self._parse_json(response)

    def try_http_post(self, url, *args, **kwargs):
        response = super().try_http_post(url, *args, **kwargs)
        return self._parse_json(response)

    def _parse_json(self, response: requests.Response):
        content_type = response.headers['Content-type']
        self.mumble_if_false(
            response.headers['Content-Type'].startswith('application/json'),
            'Invalid content type at %s: "%s", expected "application/json"' % (response.url, content_type)
        )

        try:
            result = response.json()
            logging.debug('Parsed JSON response: %s' % pprint.pformat(result))
        except json.JSONDecodeError as e:
            logging.error("Invalid JSON in response on %s: %s", response.url, str(e), exc_info=e)
            self.exit(checklib.StatusCode.MUMBLE, "Invalid JSON in response on %s" % (response.url, ))
            return

        self.check_json_response(result, response.url)

        return result

    def check_json_response(self, response: dict, url: str):
        pass

