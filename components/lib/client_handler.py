import os
import psutil
import json

from ConfigParser import ConfigParser

from logger import Logger


class ClientHandler:
    """ClientHadler class to get client's information."""

    def __init__(self):
        self.client_config_path = os.environ.get('CONFIG_FILE_PATH')
        self.config_instance = ConfigParser()
        self.config_instance.read(self.client_config_path)

        # fetching error and info log file paths
        self.error_log_file_path = self.config_instance.get(
            'settings', 'error_log_file_path')
        self.info_log_file_path = self.config_instance.get(
            'settings', 'info_log_file_path')

        self.logger_instance = Logger(**{
            'file_name': os.path.basename(self.error_log_file_path),
            'log_dir': os.path.dirname(self.error_log_file_path),
            'stream_handler': True,
            'file_handler': True, })

        self.logger_instance_info = Logger(**{
            'file_name': os.path.basename(self.info_log_file_path),
            'log_dir': os.path.dirname(self.info_log_file_path),
            'stream_handler': True,
            'file_handler': False})

    def send_client_stats(self):
        """send_client_stats method to fetch client memory/cpu usage."""
        try:
            client_stats = {}
            client_stats['cpu'] = psutil.cpu_percent()
            client_stats['memory'] = psutil.virtual_memory().percent
            return client_stats
        except Exception as error:
            self.logger_instance.logger.error(
                'ClientHadler::send_client_stats:{}'.format(
                    error.message))
            return None

    def send_process_stat(self, pid):
        """send_process_stat method for a process running at client."""
        try:
            process_instance = psutil.Process(pid)
            process_stats = {}
            process_stats['memory'] = process_instance.memory_percent()
            process_stats['cpu'] = process_instance.cpu_percent()
            return process_stats
        except Exception as error:
            self.logger_instance.logger.error(
                'ClientHadler::send_process_stat:{}'.format(
                    error.message))
            return None

    def reboot_client(self):
        """reboot_client method to reboot remote client."""
        try:
            os.system('reboot')
        except Exception as error:
            self.logger_instance.logger.error(
                'ClientHadler::reboot_client:{}'.format(
                    error.message))
            return None

    def send_camera_shot(self):
        """send_camera_shot method to get a snap from client side camera."""
        # code goes here

    def send_client_details(self):
        """send_client_details method to get details of cliet machine."""
        try:
            client_details = {
                'name': self.config_instance.get('client', 'name'),
                'id': self.config_instance.get('client', 'id')}
            return client_details
        except Exception as error:
            self.logger_instance.logger.error(
                'ClientHadler::send_client_details:{}'.format(
                    error.message))
            return None

    def process_server_message(self, message):
        """process_server_message method to fulfil server side request."""
        try:
            message = json.loads(message)
            if 'type' in message.keys():
                query_param = message['type']
                if query_param == 'action':
                    if message['name'].strip() == 'reboot':
                        response = self.reboot_client()
                        return response
                    elif message['name'].strip() == 'screenshot':
                        response = self.send_camera_shot()
                        return response
                elif query_param == 'query':
                    if message['name'] == 'client_stat':
                        response = self.send_client_stats()
                        return response
                    elif message['name'] == 'process_stat':
                        response = self.send_process_stat(
                            message['extra_params'])
                        return response
                    elif message['name'] == 'client_details':
                        response = self.send_client_details()
                        return response
                else:
                    raise Exception('invalid parameters in server message')

        except Exception as error:
            self.logger_instance.logger.error(
                'Client_Handler::process_server_message:{}'.format(
                    error.message))
            return None
