import logging

from urllib import parse_qs

from gae_python_gcm.gcm import GCMConnection, GCMMessage


def _get_values(params, key):
    return params.get(key, [])


def app(environ, start_response):
    try:
        body = environ.get('wsgi.input', '')
        if hasattr(body, 'read'):
            body = body.read()
        body = body or ''

        query_string = environ.get('QUERY_STRING', '')
        if query_string:
            body = (body + '&' + query_string) if body else query_string

        params = parse_qs(body)

        device_tokens = []
        for value in _get_values(params, 'device_tokens') + _get_values(params, 'device_token'):
            if ',' in value:
                device_tokens.extend(value.split(','))
            else:
                device_tokens.append(value)

        notification = _get_values(params, 'notification')
        notification = notification[0] if notification else None

        collapse_key = _get_values(params, 'collapse_key')
        collapse_key = collapse_key[0] if collapse_key else None

        if device_tokens and notification is not None:
            message = GCMMessage(device_tokens, notification, collapse_key=collapse_key)
            GCMConnection()._send_request(message)
    except Exception:
        logging.exception('Error in non-Django send_request handler')

    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['']
