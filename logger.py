from datetime import datetime


class Logger:
    def __init__(self, prefix=None):
        now = datetime.utcnow()
        self.prefix = prefix

    def log(self, value, **kwargs):
        now = datetime.utcnow()
        log_value = f'{now.isoformat()} | {self.prefix + ": " if self.prefix else ""}{value}'
        if kwargs:
            log_value.format(kwargs)

        self._write_log(log_value)
        print(log_value)

    @staticmethod
    def _write_log(log_value):
        now = datetime.utcnow()
        with open('coupon_clipper_log_{0}'.format(now.strftime('%Y_%m')), 'a') as file:
            file.write(log_value)
            file.write('\n')
            file.close()
