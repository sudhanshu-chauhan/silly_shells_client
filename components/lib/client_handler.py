import os
import psutil

from ConfigParser import ConfigParser

from logger import Logger

client_config_path = '../client_config.cfg'
config_instance = ConfigParser()
config_instance.read(client_config_path)

logger_instance = Logger(**{
    'file_name': 'error.log',
    'log_dir': config_instance.get('settings', 'log_dir'),
    'stream_handler': True,
    'file_handler': True,
})


class ClientHandler:
    """ClientHadler class to get client's information."""

    def __init__(self):
        pass

    def send_client_stats(self):
        """send_client_stats method to fetch client memory/cpu usage."""
        try:
            client_stats = {}
            client_stats['cpu'] = psutil.cpu_percent()
            client_stats['memory'] = psutil.virtual_memory().percent
            return client_stats
        except Exception as error:
            logger_instance.logger.error(
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
            logger_instance.logger.error(
                'ClientHadler::send_process_stat:{}'.format(
                    error.message))
            return None

    def reboot_client(self):
        """reboot_client method to reboot remote client."""
        try:
            os.system('reboot')
        except Exception as error:
            logger_instance.logger.error(
                'ClientHadler::reboot_client:{}'.format(
                    error.message))

    def send_camera_shot(self):
        """send_camera_shot method to get a snap from client side camera."""
        # code goes here

    def send_client_details(self):
        """send_client_details method to get details of cliet machine."""
        try:
            client_details = {}
            return client_details
        except Exception as error:
            logger_instance.logger.error(
                'ClientHadler::send_client_details:{}'.format(
                    error.message))
            return None
