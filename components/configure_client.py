import os
import sys
import getpass
import uuid
import json

from ConfigParser import ConfigParser
from crontab import CronTab
import requests as rq


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

    except Exception as error:
        print('Couldnt fetch token: {}'.format(error.message))


def main():
    """
    configure_clients main method to handle
    client's initial configuration.
    """
    try:
        project_component_directory = os.path.dirname(
            os.path.abspath(__file__))

        # checking config file path
        config_file_path = os.path.join(
            project_component_directory, 'client_config.cfg')

        if not os.path.exists(config_file_path):
            print('configuration file not found in the components directory')
            sys.exit(1)

        # setting log directory

        config_instance = ConfigParser()
        config_instance.read(config_file_path)

        home_dir = os.environ.get('HOME')
        error_log_file_path = os.path.join(home_dir,
                                           'logs',
                                           'silly_shell_client_error.log')
        info_log_file_path = os.path.join(home_dir,
                                          'logs',
                                          'silly_shell_client_info.log')
        print('setting error and info log file paths!')
        print(error_log_file_path)
        print(info_log_file_path)
        config_instance.set(
            'settings', 'error_log_file_path', error_log_file_path)
        config_instance.set(
            'settings', 'info_log_file_path', info_log_file_path)

        url = config_instance.get('server', 'url')
        port = config_instance.get('server', 'port')
        api_protocol = config_instance.get('settings', 'api_protocol').strip()
        auth_api_endpoint = config_instance.get(
            'settings', 'auth_api_endpoint').strip()

        credentials = {}

        # setting client token
        print('client credentials...')
        credentials['email'] = str(raw_input('email: '))
        credentials['password'] = getpass.getpass('password: ')

        token = get_token(api_protocol,
                          url,
                          port,
                          auth_api_endpoint,
                          **credentials)
        if token is not None:
            print('client credentials authenticated successfully!')
            print('setting client details...')
            client_name = str(raw_input('enter a client name:'))
            config_instance.set('client', 'name', client_name)
            client_unique_id = str(uuid.uuid4())
            print('setting client unique id:{}'.format(client_unique_id))
            config_instance.set('client', 'id', client_unique_id)
            config_instance.set('client', 'token', token)
            with open(config_file_path, 'wb') as config_file:
                config_instance.write(config_file)
        else:
            print('could not fetch token, try credentials again')
            sys.exit(1)

        # setting cron for the client machine
        print('setting up client.py as auto reboot cron job...')
        current_user_cron = CronTab(user=getpass.getuser())
        client_script_path = os.path.join(
            project_component_directory, 'client.py')
        cron_job_command = '{}'.format(client_script_path)
        job = current_user_cron.new(command=cron_job_command)
        job.every_reboot()
        if job.is_valid():
            current_user_cron.write_to_user()
            print('All Set. Adios Muchachos!')
        else:
            print('error in cron configuration! exiting...')

    except Exception as error:
        print(error.message)


if __name__ == '__main__':
    main()
