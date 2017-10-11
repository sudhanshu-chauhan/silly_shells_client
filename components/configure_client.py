import getpass

from ConfigParser import ConfigParser

from clients import Client


def main():
    """
    configure_clients main method to handle
    client's initial configuration.
    """
    try:
        config_instance = ConfigParser()
        config_instance.read('./client_config.cfg')

        url = config_instance.get('server', 'url')
        port = config_instance.get('server', 'port')
        client_instance = Client(auth_url='http://{}:{}/get_token'.format(
            url, port))
        credentials = {}

        print('client credentials...')
        credentials['email'] = str(raw_input('email: '))
        credentials['password'] = getpass.getpass('password: ')
        
        token = client_instance.get_token(**credentials)
        client_instance.set_token(token)

    except Exception as error:
        print(error.message)
