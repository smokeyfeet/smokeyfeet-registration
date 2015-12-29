from django.conf import settings
import jwt


def make_token(registration):
    claims = {'registration_ref': registration.ref}
    encoded = jwt.encode(claims, settings.SECRET_KEY, algorithm='HS256')
    return str(encoded, 'ascii')
