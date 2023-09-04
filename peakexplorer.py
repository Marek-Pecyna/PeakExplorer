"""
Peak Explorer 2023
Analyzes and visualizes HPLC-MS Data given in simple ascii format (CSV format)

Good example values for example file 'Beispiel_asci.ascii':
mass trace: 465 Da
elution time trace: 4.2 Min

mass trace: 425 Da
elution time trace: 13.2 Min

Command-Line arguments:
    -debug: Enable Debug (level 10) for console and log_file
    -log_file <filename>
"""

import logging
import sys

from Controller import Controller
from Constants import APP_TITLE, VERSION, SETTINGS_FILENAME
from View import View


__author__ = "Dr. Marek Pecyna, https://daten-entdecker.de/"


def add_logging_level(level_name, level_num, method_name=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.
    This method is copied from Stack Overflow post https://stackoverflow.com/a/35804945
    """
    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    if not method_name:
        method_name = level_name.lower()
    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)
    return


def setup_logging(console_level, file_level=None, log_file='running_explorer.log'):
    """ Setup logging for whole application """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)-8s %(name)s.%(funcName)s(): %(message)s')

    # Add new logging level 'NOTE' between INFO (20) and WARNING (30)
    NOTE = logging.INFO + 5
    add_logging_level('NOTE', NOTE)

    # Console logging
    sh = logging.StreamHandler()
    sh.setLevel(console_level)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # File logging
    if file_level:
        fh = logging.FileHandler(log_file, mode="w")
        fh.setLevel(file_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger


def main():
    # Set logging defaults
    db_console = 30  # equals logging.WARNING
    db_file = None  # -> no logging in file
    log_file = 'running_explorer.log'

    # Parse command-line arguments for logging
    for index, entry in enumerate(sys.argv):
        if entry == "-debug":
            db_console = 10
            db_file = 10
            if index + 1 < len(sys.argv):
                db_console = int(sys.argv[index + 1])
                db_file = int(sys.argv[index + 1])
        if entry == "-log_file":
            if index + 1 < len(sys.argv):
                log_file = sys.argv[index + 1]


    # Start logger
    logger = setup_logging(db_console, db_file, log_file)

    text = [f'Program:   {APP_TITLE} Version {VERSION}',
            f'Author:    {__author__}',
            f'Startfile: {__file__}']
    logging.log(25, "_" * len(max(text)))
    for line in text:
        logging.log(25, line)
    logging.log(25, "_" * len(max(text)))
    logging.log(25, f'START {Controller.__module__}')
    controller = Controller(settings_filename=SETTINGS_FILENAME)
    logging.log(25, f'START {View.__module__}')
    view = View(title=f"{APP_TITLE} {VERSION}", settings=controller.settings)
    controller.set_view(view)
    logging.log(25, f'EXECUTE {controller.__module__}.{controller.mainloop.__name__}...')
    controller.mainloop()
    logging.log(25, f'Program finished. Good Bye!')


if __name__ == '__main__':
    main()
