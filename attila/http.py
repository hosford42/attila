import ctypes
import time

from . import files
from .files import Path


__author__ = 'Aaron Hosford'


class HTTPFSConnector(files.FSConnector):

    def __init__(self, initial_cwd=None):
        super().__init__(http_fs_connection, initial_cwd)

    def is_configured(self):
        return True  # Always in a usable state.


# noinspection PyPep8Naming,PyAbstractClass
class http_fs_connection(files.fs_connection):
    """
    An http_fs_connection handles the underlying interactions with a remote file system accessed via HTTP on
    behalf of Path instances.
    """

    def __init__(self, connector=None):
        if connector is None:
            connector = HTTPFSConnector()
        else:
            assert isinstance(connector, HTTPFSConnector)
        super().__init__(connector)
        super().open()  # http fs connections are always open.

    def open(self):
        pass  # http fs connections are always open.

    def close(self):
        pass  # http fs connections are always open.

    def __repr__(self):
        return type(self).__name__ + '()'

    def __eq__(self, other):
        if not isinstance(other, files.fs_connection):
            return NotImplemented
        return isinstance(other, http_fs_connection)

    def open_file(self, path, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True,
                  opener=None):
        """
        Open the file.

        :param path: The path to operate on.
        :param mode: The file mode.
        :param buffering: The buffering policy.
        :param encoding: The encoding.
        :param errors: The error handling strategy.
        :param newline: The character sequence to use for newlines.
        :param closefd: Whether to close the descriptor after the file closes.
        :param opener: A custom opener.
        :return: The opened file object.
        """
        path = self.check_path(path)

        if mode not in ('r', 'rb'):
            raise ValueError("Unsupported mode: " + repr(mode))

        # We can't work directly with an HTTP file using URLDownloadToFileW(). Instead, we will create a temp file and
        # return it as a proxy.
        temp_path = files.local_fs_connection.get_temp_file_path(self.name(path))

        # http://msdn.microsoft.com/en-us/library/ie/ms775123(v=vs.85).aspx
        result = ctypes.windll.urlmon.URLDownloadToFileW(0, path, str(temp_path), 0, 0)

        if result == 1:
            raise MemoryError(
                "Insufficient memory available to download " + path + ". (Return code 1)"
            )
        elif result != 0:
            raise RuntimeError(
                "Unspecified error while trying to download " + path + ". (Return code " + str(result) + ")"
            )
        elif not temp_path.is_file:
            raise FileNotFoundError(
                "File appeared to download successfully from " + path + " but could not be found afterward."
            )

        return files.ProxyFile(Path(path, self), mode, buffering, encoding, errors, newline, closefd, opener,
                               proxy_path=temp_path, writeback=None)
