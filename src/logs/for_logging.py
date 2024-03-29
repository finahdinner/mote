import logging
from enum import Enum
from discord.ext import commands


class ExecutionOutcome(Enum):
    ERROR = 2
    WARNING = 1
    DEFAULT = 0
    SUCCESS = -1


class MyLogger:
    def __init__(self, file_name, log_file_path):
        self.file_name = file_name
        self.log_file_path = log_file_path # log file path

        # logger
        self.logger = logging.getLogger(self.file_name)
        self.logger.setLevel(logging.DEBUG) # unless a handler is specified otherwise, will log DEBUG and above

        # logger handler for the log file
        self.file_handler = logging.FileHandler(self.log_file_path)
        self.file_handler.setLevel(logging.ERROR) # only log to file for ERRORS and above
        self.file_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s') # format of log lines
        self.file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(self.file_handler)

        # logger handler for the to console - will log all things (debug and above)
        self.stream_handler = logging.StreamHandler()
        self.stream_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        self.stream_handler.setFormatter(self.stream_formatter)
        self.logger.addHandler( self.stream_handler)

    def log_message(self, ctx: commands.Context, bot_message: str, exec_outcome=ExecutionOutcome.DEFAULT) -> None:
        single_line_bot_message = bot_message.replace('\n', ' ')
        log_msg = f"({ctx.guild}, {ctx.channel}) {ctx.message.content} --> {single_line_bot_message}"
        if exec_outcome == ExecutionOutcome.DEFAULT or exec_outcome == ExecutionOutcome.SUCCESS:
            self.logger.info(log_msg)
        elif exec_outcome == ExecutionOutcome.WARNING:
            self.logger.warning(log_msg)
        elif exec_outcome == ExecutionOutcome.ERROR:
            self.logger.error(log_msg)