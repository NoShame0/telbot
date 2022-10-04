"""
Threading of checking time notification
"""

import datetime
from config import config
import threading


class TimeChecker:

    def __init__(self, bot):
        self.bot = bot

    def time_check(self):
        # infinity loop for checkin user time last message
        while True:
            now = datetime.datetime.now()
            now = now - datetime.timedelta(microseconds=now.microsecond)

            # checking every chat
            for chat_id, options in config.items():
                if options['start'] and \
                        now == options['time_last_message'] + datetime.timedelta(hours=options['interval']):
                    self.bot.send_message(chat_id, f'💻 Пора учиться, {options["first_name"]}! 🖊')
                    config[chat_id]['time_last_message'] = now

    def start(self):

        thread = threading.Thread(target=self.time_check)
        thread.start()
