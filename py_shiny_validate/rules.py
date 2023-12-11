from typing import Callable
import re
import numpy as np


def input_provided(val: any):
    print(val)
    if val is None:
        return False
    if isinstance(val, Exception):
        return False
    return True


def sv_required(message: str = "Required", test: Callable = input_provided):
    """
    Generate a validation function that ensures an input value is present.

    Parameters
    ----------
    message : str, optional
        The validation error message to be displayed if the test does not pass, by default "Required"
    test : function, optional
        A function that tests the input value, by default input_provided

    Returns
    -------
    function
        A function that takes an input value and returns the error message if the test does not pass.

    Raises
    ------
    ValueError
        If the test argument is not a function.
    """
    if not callable(test):
        raise ValueError("`test` argument must be a function")

    def inner(value):
        if not test(value):
            return message

    return inner


def sv_optional(test: Callable = input_provided):
    """
    Generate a validation function that indicates an input is allowed to not be present.
    If an sv_optional rule sees that an input is not present, subsequent rules for that input are skipped and the input is considered valid.
    Otherwise, the rule simply passes. sv_optional will never return a validation error/message.

    Parameters
    ----------
    test : function, optional
        A function that tests the input value, by default input_provided

    Returns
    -------
    function
        A function that takes an input value and returns None if the test does not pass.

    Raises
    ------
    ValueError
        If the test argument is not a function.
    """
    if not callable(test):
        raise ValueError("`test` argument must be a function")

    def inner(value):
        if not test(value):
            return None

    return inner


def sv_regex(pattern: str, message: str, ignore_case: bool = False):
    """
    Generate a validation function that checks if the input value matches the given regex pattern.

    Parameters
    ----------
    pattern : str
        The regex pattern to match.
    message : str
        The error message to return if the input value does not match the pattern.
    ignore_case : bool, optional
        If True, the regex match is case-insensitive. Default is False.

    Returns
    -------
    function
        A function that takes an input value and returns the error message if the input value does not match the pattern.
    """
    import re

    flags = re.IGNORECASE if ignore_case else 0

    def inner(value: str):
        if not re.search(pattern, value, flags=flags):
            return message

    return inner


def sv_email(
    message: str = "Not a valid email address",
    allow_multiple: bool = False,
    allow_na: bool = False,
):
    """
    Generate a validation function that checks if the input value is a valid email address.

    Parameters
    ----------
    message : str
        The error message to return if the input value is not a valid email address.
    allow_multiple : bool, optional
        If True, multiple email addresses are allowed. Default is False.
    allow_na : bool, optional
        If True, NA values are allowed. Default is False.

    Returns
    -------
    function
        A function that takes an input value and returns the error message if the input value is not a valid email address.
    """
    import re

    def inner(value: str):
        # Regular expression taken from
        # https://www.nicebread.de/validating-email-adresses-in-r/
        pattern = "^\\s*[A-Z0-9._%&'*+`/=?^{}~-]+@[A-Z0-9.-]+\\.[A-Z0-9]{2,}\\s*$"
        flags = re.IGNORECASE

        if allow_na and value is None:
            return

        if allow_multiple:
            emails = value.split(",")
            for email in emails:
                if not re.search(pattern, email.strip(), flags=flags):
                    return message
        else:
            if not re.search(pattern, value, flags=flags):
                return message

    return inner


def sv_url(
    message: str = "Not a valid URL",
    allow_multiple: bool = False,
    allow_na: bool = False,
):
    """
    Generate a validation function that checks if the input value is a valid URL.

    Parameters
    ----------
    message : str
        The error message to return if the input value is not a valid URL.
    allow_multiple : bool, optional
        If True, multiple URLs are allowed. Default is False.
    allow_na : bool, optional
        If True, NA values are allowed. Default is False.

    Returns
    -------
    function
        A function that takes an input value and returns the error message if the input value is not a valid URL.
    """
    import re

    def inner(value: str):
        # Regular expression taken from
        # https://gist.github.com/dperini/729294
        pattern = "^(?:(?:http(?:s)?|ftp)://)(?:\\S+(?::(?:\\S)*)?@)?(?:(?:[a-z0-9\u00a1-\uffff](?:-)*)*(?:[a-z0-9\u00a1-\uffff])+)(?:\\.(?:[a-z0-9\u00a1-\uffff](?:-)*)*(?:[a-z0-9\u00a1-\uffff])+)*(?:\\.(?:[a-z0-9\u00a1-\uffff]){2,})(?::(?:\\d){2,5})?(?:/(?:\\S)*)?$"
        flags = re.IGNORECASE

        if allow_na and value is None:
            return

        if allow_multiple:
            urls = value.split(",")
            for url in urls:
                if not re.search(pattern, url.strip(), flags=flags):
                    return message
        else:
            if not re.search(pattern, value, flags=flags):
                return message

    return inner


def sv_integer(
    message: str = "An integer is required",
    allow_multiple: bool = False,
    allow_na: bool = False,
    allow_nan: bool = False,
):
    """
    Generate a validation function that checks if the input value is an integer.

    Parameters
    ----------
    message : str
        The error message to return if the input value is not an integer.
    allow_multiple : bool, optional
        If True, multiple integers are allowed. Default is False.
    allow_na : bool, optional
        If True, NA values are allowed. Default is False.
    allow_nan : bool, optional
        If True, NaN values are allowed. Default is False.

    Returns
    -------
    function
        A function that takes an input value and returns the error message if the input value is not an integer.
    """

    def inner(value: str):
        if allow_na and value is None:
            return
        if allow_nan and np.isnan(value):
            return

        if allow_multiple:
            integers = value.split(",")
            for integer in integers:
                if not re.search(r"^-?\d+$", integer.strip()):
                    return message
        else:
            if not re.search(r"^-?\d+$", value):
                return message

    return inner
