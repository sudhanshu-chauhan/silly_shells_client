import os
import json

import websocket
import requests as rq
from ConfigParser import ConfigParser

from lib.logger import Logger
from lib.client_handler import ClientHandler

client_config_path = os.environ.get('CONFIG_FILE_PATH')
config_instance = ConfigParser()
config_instance.read(client_config_path)

error_log_file_path = config_instance.get(
    'settings', 'error_log_file_path').strip()

info_log_file_path = config_instance.get(
    'settings', 'info_log_file_path').strip()

logger_instance = Logger(**{
    'file_name': os.path.basename(error_log_file_path),
    'log_dir': os.path.dirname(error_log_file_path),
    'stream_handler': True,
    'file_handler': True})

logger_instance_info = Logger(**{
    'file_name': os.path.basename(info_log_file_path),
    'log_dir': os.path.dirname(info_log_file_path),
    'file_handler': False,
    'stream_handler': True})

client_handler_instance = ClientHandler()


def get_token(api_protocol, server, port, auth_api_endpoint, **credential):
    try:
        if 'email' not in credential or 'password' not in credential:
            raise Exception('invalid credential param')
        auth_url = '{}://{}:{}/{}'.format(api_protocol,
                                          server,
                                          port,
                                          auth_api_endpoint)

        response = rq.post(auth_url, data=json.dumps(credential))
        if response.status_code == 200:
            return response.json()['token']
        else:
            return None
    except Exception:
        return None


class ClientSocketHandler:
    """ClientSocketHandler class for client socket events."""

    def __init__(self):
        pass

    def on_open(self, websocket_instance):
        try:
            logger_instance_info.logger.info('socket opened')
        except Exception as error:
            logger_instance.logger.error(
                'ClientSocketHandler::on_open:{}'.format(
                    error.message))

    def on_message(self, websocket_instance, message):
        """on_message event handler for client socket."""
        try:
            response = client_handler_instance.process_server_message(
                message=message)
            if response is not None:
                websocket_instance.send(response)
            else:
                websocket_instance.send('client unable to parse params.')

        except Exception as error:
            logger_instance.logger.error(
                'ClientSocketHandler::on_message:{}'.format(
                    error.message))

    def on_error(self, websocket_instance, error):
        """on_error event handler for client socket."""
        logger_instance.logger.error(
            'ClientSocketHandler::on_error:{}'.format(
                error))

    def on_close(self, websocket_instance):
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
    try:
        header = {'Authorization': config_instance.get('client', 'token')}
        server = config_instance.get('server', 'url')
        port = config_instance.get('server', 'port')
        websocket.enableTrace(True)
        client_socket_handler_instance = ClientSocketHandler()
        ws = websocket.WebSocketApp(
            'ws://{}:{}/sock_server/'.format(server,
                                             port),
            header=header,
            on_message=client_socket_handler_instance.on_message,
            on_error=client_socket_handler_instance.on_error,
            on_close=client_socket_handler_instance.on_close)

        ws.on_open = client_socket_handler_instance.on_open
        ws.run_forever()
    except Exception as error:
        logger_instance.logger.error(
            'client::main:{}'.format(error.message))
