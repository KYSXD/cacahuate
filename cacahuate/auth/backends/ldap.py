from ldap3 import Server, Connection, ALL

from cacahuate.auth.base import BaseAuthProvider
from cacahuate.errors import AuthenticationError
from cacahuate.http.wsgi import app
from cacahuate.models import User


class LdapAuthProvider(BaseAuthProvider):

    def authenticate(self, **credentials):
        if 'username' not in credentials:
            raise AuthenticationError({
                'description': 'username not sent',
                'code': 'validation.required',
                'where': 'request.body.username.required',
            })
        if 'password' not in credentials:
            raise AuthenticationError({
                'description': 'password not sent',
                'code': 'validation.required',
                'where': 'request.body.password.required',
            })

        server_uri = app.config['LDAP_URI']
        use_ssl = app.config['LDAP_SSL']
        base = app.config['LDAP_BASE']
        domain = app.config['LDAP_DOMAIN']

        # Use credentials to authenticate
        username = credentials['username']
        password = credentials['password']
        if 'domain' in credentials:
            domain = credentials['DOMAIN']

        # Connect & query ldap
        server = Server(
            server_uri,
            get_info=ALL,
            use_ssl=use_ssl,
        )

        conn = Connection(
            server,
            user='{}\\{}'.format(domain, username),
            password=password,
            auto_bind=True,
        )

        conn.search(
            base,
            '(CN={})'.format(username),
            attributes=['mail', 'givenName', 'sn']
        )

        entry = conn.entries[0]

        identifier = '{}\\{}'.format(domain, username)
        email = str(entry.mail)
        name = str(entry.givenName)
        surname = str(entry.sn)
        fullname = '{} {}'.format(name, surname)

        # fetchs redis mirror user if there is None then creates one
        user = User.get_by('identifier', identifier)

        if user is None:
            user = User(
                identifier=identifier,
                email=email,
                fullname=fullname
            ).save()

        return user
