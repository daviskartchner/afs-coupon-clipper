import os
from datetime import datetime
from zoneinfo import ZoneInfo

class Logger:
    def __init__(self, prefix=None, iana_name = 'America/Denver'):
        if not os.path.exists('logs'):
            os.mkdir('logs')

        self.timezone = ZoneInfo(iana_name)
        self.prefix = prefix

    def log(self, value, **kwargs):
        now_local = datetime.now().astimezone(self.timezone)
        log_value = f'{now_local.strftime("%Y-%m-%d %H:%M:%S")} | {self.prefix + ": " if self.prefix else ""}{value}'
        if kwargs:
            log_value.format(kwargs)

        self._write_log(log_value)
        print(log_value)

    @staticmethod
    def _write_log(log_value):
        now = datetime.utcnow()
        with open('logs/logfile_{0}.log'.format(now.strftime('%Y_%m')), 'a+') as file:
            file.write(log_value)
            file.write('\n')
            file.close()
