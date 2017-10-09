import json

import websocket
import requests as rq
from ConfigParser import ConfigParser

from lib.logger import Logger


client_config_path = './client_config.cfg'
config_instance = ConfigParser()
config_instance.read(client_config_path)

logger_instance = Logger(**{
    'file_name': 'error.log',
    'log_dir': config_instance.get('settings', 'log_dir'),
    'stream_handler': True,
    'file_handler': True,
})

logger_instance_info = Logger(**{
    'file_name': 'client.log',
    'log_dir': config_instance.get('settings', 'log_dir'),
    'file_handler': False,
    'stream_handler': True
})


class Client:

    def __init__(self, server=None, port=80, https_enabled=False):
        try:
            if server is None:
                raise Exception('server ip address not provided')
                self.auth_api_endpoint = 'get_token/'
                self.server = server
                self.port = port
                if https_enabled:
                    self.api_protocol = 'https'
                else:
                    self.api_protocol = 'http'
        except Exception as error:
            logger_instance.logger.error(
                'Client::__init__:{}'.format(error.message))

    def get_token(self, **credential):
        try:
            if 'email' not in credential or 'password' not in credential:
                raise Exception('invalid credential param')
            auth_url = '{}://{}:{}/{}'.format(self.api_protocol,
                                              self.server,
                                              self.port,
                                              self.auth_api_endpoint)

            response = rq.post(auth_url, data=json.dumps(credential))
            if response.status_code == 200:
                return response.json()['token']
            else:
                return None

        except Exception as error:
            logger_instance.logger.error(
                'Client::get_token:{}'.format(error.message))
            return None

    def set_token(self, token):
        """set_token method to set token in config file."""
        try:
            config_instance.set('client', 'token', token)
            return True
        except Exception as error:
            logger_instance.logger.error(
                'Client::set_token:{}'.format(error.message))
            return False


class ClientSocketHandler:
    """ClientSocketHandler class for client socket events."""

    def __init__(self):
        pass

    @staticmethod
    def on_open(websocket_instance):
        try:
            logger_instance_info.logger.info('socket opened')
        except Exception as error:
            logger_instance.logger.error(
                'ClientSocketHandler::on_open:{}'.format(
                    error.message))

    @staticmethod
    def on_message(websocket_instance, message):
        """on_message event handler for client socket."""
        try:
            print(message)
        except Exception as error:
            logger_instance.logger.error(
                'ClientSocketHandler::on_message:{}'.format(
                    error.message))

    @staticmethod
    def on_error(websocket_instance, error):
        """on_error event handler for client socket."""
        logger_instance.logger.error(
            'ClientSocketHandler::on_error:{}'.format(
                error))

    @staticmethod
    def on_close(websocket_instance):
        """on_close event handler for client socket."""
        try:
            print('[*]client socket closed...')
        except Exception as error:
            logger_instance.logger.error(
                'ClientSocketHandler::on_error:{}'.format(
                    error.message))


def on_open(ws):
    logger_instance_info.logger.info('opened socket connection')

if __name__ == '__main__':
    client_instance = Client(server=config_instance.get('server', 'url'),
                             port=int(config_instance.get('server', 'port')))
    header = {'Authorization': config_instance.get('client', 'token')}
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        'ws://{}:{}/sock_server/'.format(client_instance.server,
                                         client_instance.port),
        header=header,
        on_message=ClientSocketHandler.on_message,
        on_error=ClientSocketHandler.on_error,
        on_close=ClientSocketHandler.on_close)
    ws.on_open = on_open
    ws.run_forever()
