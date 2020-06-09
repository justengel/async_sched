import datetime
import sys
import traceback


__all__ = ['ScheduleError', 'print_exception', 'get_traceback',
           'is_ignored', 'ignore_exception', 'stop_ignore_exception']


# ========== Exception Handling ==========
IGNORE_PRINT_EXCEPTION = []


class ScheduleError(Exception):
    pass


def print_exception(exc, msg=None, error_cls=ScheduleError):
    """Print the given exception. If a message is given it will be prepended to the exception message with a \n.

    Args:
        exc (Exception): Exception that was raised.
        msg (str)[None]: Additional message to prepend to the exception.
        error_cls (Exception)[ServiceError]: New Exception class to print the exception as.
    """
    # Prepend the message to the exception if given
    if msg:
        msg = "\n".join((msg, str(exc)))
    else:
        msg = str(exc)

    if not is_ignored(msg, exc):
        exc_tb = get_traceback(exc)
        traceback.print_exception(error_cls, error_cls(msg), exc_tb)


def get_traceback(exc=None):
    """Get the exception traceback or the system traceback."""
    _, _, sys_tb = sys.exc_info()
    try:
        return exc.__traceback__
    except (AttributeError, Exception):
        return sys_tb


def is_ignored(msg=None, exc=None):
    """Return if a message should be ignored.

    Args:
        msg (str)[None]: String message to check if ignored
        exc (Exception)[None]: Exception to check if ignored (also checks if exception class is ignored).
    """
    # Get the exception class to check the ignore
    exc_cls = None
    if isinstance(exc, BaseException):
        exc_cls = type(exc)

    ignore_msg = msg and msg in IGNORE_PRINT_EXCEPTION
    ignore_exc = exc is not None and exc in IGNORE_PRINT_EXCEPTION
    ignore_exc_cls = exc_cls is not None and exc_cls in IGNORE_PRINT_EXCEPTION
    return ignore_msg or ignore_exc or ignore_exc_cls


def ignore_exception(exc):
    """Ignore the given exception, exception message."""
    if exc not in IGNORE_PRINT_EXCEPTION:
        IGNORE_PRINT_EXCEPTION.append(exc)


def stop_ignore_exception(exc, msg=None):
    """Stop ignoring an exception.

    Args:
        exc (Exception/str): Exception to stop ignoring
        msg (str)[None]: Message text to stop ignoring
    """
    if msg:
        exc = "\n".join((msg, str(exc)))

    try:
        IGNORE_PRINT_EXCEPTION.remove(exc)
    except (AttributeError, ValueError, TypeError, Exception):
        pass
    try:
        IGNORE_PRINT_EXCEPTION.remove(msg)
    except (AttributeError, ValueError, TypeError, Exception):
        pass
