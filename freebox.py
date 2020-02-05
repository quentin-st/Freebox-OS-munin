import os
import json
import sys
import requests
import socket

from munin.util import *

freebox_config_file = os.path.join(os.path.dirname(__file__), 'freebox.json')
app_id = 'freebox-revolution-munin'  # Script legacy name. Changing this would break authentication
app_name = 'Freebox-OS-munin'
app_version = '1.0.0'
device_name = socket.gethostname()


class FreeboxNoState(Exception):
    pass


class Freebox:
    app_token = None
    session_challenge = None
    session_token = None

    def api_get_info(self):
        uri = self.protocol + '://mafreebox.freebox.fr/api_version'
        r = requests.get(uri, verify=self.root_ca)
        r_json = r.json()
        return r_json

    def get_api_call_uri(self, endpoint):
        r_json = self.api_get_info()
        api_base_url = r_json['api_base_url']
        api_version = r_json['api_version']
        major_api_version = re.search(r'\d+', api_version).group()
        return self.protocol + '://mafreebox.freebox.fr' + api_base_url + 'v' + major_api_version + '/' + endpoint

    def save(self):
        with open(freebox_config_file, 'w') as fh:
            json.dump(self.__dict__, fh)

    def retrieve(self):
        try:
            with open(freebox_config_file, 'r') as fh:
                self.__dict__ = json.load(fh)
        except FileNotFoundError as ex:
            raise FreeboxNoState() from ex

        if 'root_ca' in self.__dict__:
            # compute the full filename
            self.root_ca = os.path.join(os.path.dirname(__file__), self.root_ca)
        else:
            # backward compatibility with old config file
            self.root_ca = ''
            self.protocol = 'http'

    def api_open_session(self):
        # Retrieve challenge
        uri = self.get_api_call_uri('login/')
        r = requests.get(uri, verify=self.root_ca)
        r_json = r.json()

        if not r_json['success']:
            print('Could not retrieve challenge when opening session: {}'.format(r_json['msg']))
            sys.exit(1)

        challenge = r_json['result']['challenge']
        self.session_challenge = challenge

        # Open session
        uri += 'session/'
        password = encode_app_token(self.app_token, challenge)
        r = requests.post(uri, json={
            'app_id': app_id,
            'password': password
        }, verify=self.root_ca)
        r_json = r.json()

        if not r_json['success']:
            print('Could not open session: {}'.format(r_json['msg']))
            sys.exit(1)

        session_token = r_json['result']['session_token']
        self.session_token = session_token
        self.save()

    def api(self, endpoint, params=None):
        uri = self.get_api_call_uri(endpoint)

        # Build request
        r = requests.get(uri, params=params, headers={
            'X-Fbx-App-Auth': self.session_token
        }, verify=self.root_ca)
        r_json = r.json()

        if not r_json['success']:
            if r_json['error_code'] == 'auth_required':
                # Open session and try again
                self.api_open_session()
                return self.api(endpoint, params)
            else:
                # Unknown error (http://dev.freebox.fr/sdk/os/login/#authentication-errors)
                message = 'Unknown API error "{}" on URI {} (endpoint {})'.format(
                    r_json['error_code'],
                    uri,
                    endpoint
                )
                try:
                    print('{}: {}'.format(message, r_json['msg']))
                except UnicodeEncodeError:
                    print('{}. Plus, we could not print the error message correctly.'.format(
                        message
                    ))
                sys.exit(1)

        return r_json.get('result', '')

    def api_get_connected_disks(self):
        disks = self.api('storage/disk/')

        # Define a display name for each disk
        for disk in disks:
            name = disk.get('model')

            # Disk does not provide its model, and has exactly one partition:
            if len(name) == 0 and len(disk.get('partitions')) == 1:
                name = disk.get('partitions')[0].get('label')

            # Could not determine name from partition, try to use serial
            if len(name) == 0:
                name = disk.get('serial')

            # In last resort, use disk id
            if len(name) == 0:
                name = disk.get('id')

            slug = slugify(name)
            name += ' ({})'.format(disk.get('type'))

            disk['slug'] = slug
            disk['display_name'] = name

        return disks

    def api_authorize(self):
        print('Authorizing...')

        def authorize():
            return requests.post(uri, json={
                'app_id': app_id,
                'app_name': app_name,
                'app_version': app_version,
                'device_name': device_name
            }, verify=root_ca)

        # try to use https
        self.protocol = 'https'

        # no CA found yet
        self.root_ca = ''

        # compute URI using https
        uri = self.get_api_call_uri('login/authorize/')
        # find the root CA to use
        for root_ca in ['Freebox ECC Root CA.pem', 'Freebox Root CA.pem']:
            try:
                r = authorize()
                print("Using", root_ca)
                self.root_ca = root_ca
                break
            except requests.exceptions.SSLError:
                print("KO for", root_ca)

        if self.root_ca is '':
            print('Warning: using unsecure communication!')
            self.protocol = 'http'
            # re-compute URI using http
            uri = self.get_api_call_uri('login/authorize/')
            r = authorize()

        r_json = r.json()

        if not r_json['success']:
            print('Error while authenticating: {}'.format(r_json))
            return 1

        app_token = r_json['result']['app_token']
        track_id = r_json['result']['track_id']

        # Watch for token status
        print('Waiting for you to push the "Yes" button on your Freebox')

        challenge = None
        while True:
            r2 = requests.get(uri + str(track_id), verify=self.root_ca)
            r2_json = r2.json()
            status = r2_json['result']['status']

            if status == 'pending':
                sys.stdout.write('.')
                sys.stdout.flush()
            elif status == 'timeout':
                print('\nAuthorization request timeouted. Re-run this script, but please go faster next time')
                return 1
            elif status == 'denied':
                print('\nYou denied authorization request.')
                return 1
            elif status == 'granted':
                challenge = r2_json['result']['challenge']
                break

        self.app_token = app_token
        self.session_challenge = challenge
        self.save()

        # That's a success
        print('\nSuccessfully authenticated script. Exiting.')

        return 0


def encode_app_token(app_token, challenge):
    import hashlib
    import hmac

    return hmac.new(app_token.encode('utf-8'), challenge.encode('utf-8'), hashlib.sha1).hexdigest()
