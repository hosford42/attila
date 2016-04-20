import logging

from ..abc.configurations import Configurable
from ..abc.notifications import Notifier
from ..configurations import ConfigLoader
from ..exceptions import OperationNotSupportedError, verify_type


__author__ = 'Aaron Hosford'


class LogNotifier(Notifier, Configurable):
    """
    A log notifier passes incoming notifications to a logger.
    """

    @classmethod
    def load_config_value(cls, config_loader, value, *args, **kwargs):
        """
        Load a class instance from the value of a config option.

        :param config_loader: A ConfigLoader instance.
        :param value: The string value of the option.
        :return: A new instance of this class.
        """
        verify_type(config_loader, ConfigLoader)
        verify_type(value, str, non_empty=True)

        if '@' in value:
            name, level = value.split('@')
            if level.isdigit():
                level = int(level)
            else:
                level = getattr(logging, level.upper())
                assert isinstance(level, int)
        else:
            name = value
            level = logging.INFO

        logger = logging.getLogger(name)

        return cls(*args, logger=logger, level=level, **kwargs)

    @classmethod
    def load_config_section(cls, config_loader, section, *args, **kwargs):
        """
        Load a class instance from a config section.

        :param config_loader: A ConfigLoader instance.
        :param section: The name of the section.
        :return: A new instance of this class.
        """
        verify_type(config_loader, ConfigLoader)
        assert isinstance(config_loader, ConfigLoader)
        verify_type(section, str, non_empty=True)

        name = config_loader.load_option(section, 'Name', str)
        level = config_loader.load_option(section, 'Level', str, 'INFO')

        if level.isdigit():
            level = int(level)
        else:
            level = getattr(logging, level.upper())
            assert isinstance(level, int)

        logger = logging.getLogger(name)

        return cls(*args, logger=logger, level=level, **kwargs)

    def __init__(self, logger, level=None):
        if isinstance(logger, str):
            verify_type(logger, str, non_empty=True)
            logger = logging.getLogger(logger)
        verify_type(logger, logging.Logger)

        if level is None:
            level = logging.INFO
        verify_type(level, int)

        super().__init__()

        self._logger = logger
        self._level = level

    @property
    def logger(self):
        """The logger this notifier sends to."""
        return self._logger

    @property
    def level(self):
        """The logging level this notifier sends at."""
        return self._level

    def __call__(self, *args, attachments=None, **kwargs):
        """
        Send a notification on this notifier's channel.

        :param attachments: The file attachments, if any, to include in the notification. (Not supported.)
        :return: None
        """
        if attachments is not None:
            raise OperationNotSupportedError("File attachments are unsupported.")
        self._logger.log(self._level, *args, **kwargs)