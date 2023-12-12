from typing import Callable
import re
import numpy as np

err_msg_zero_length_value = "Must not contain zero values."
err_msg_allow_multiple = "Must not contain multiple values."
err_msg_allow_na = "Must not contain `NA` values."
err_msg_allow_nan = "Must not contain `NaN` values."
err_msg_allow_infinite = "Must not contain infinite values."


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


def compose_rules(*args):
    """
    Combine multiple validation rules into one.

    Parameters
    ----------
    *args : functions
        Validation functions to combine.

    Returns
    -------
    function
        A function that takes an input value and checks it against all the provided validation functions.
        Returns the error message from the first validation function that fails, or None if all validation functions pass.
    """
    rule_fns = [arg for arg in args if callable(arg)]

    def inner(value: str):
        for rule_fn in rule_fns:
            res = rule_fn(value)
            if res is not None:
                return res

    return inner


def sv_basic(allow_multiple: bool, allow_na: bool, allow_nan: bool, allow_inf: bool):
    """
    Basic validation function.

    Parameters
    ----------
    allow_multiple : bool
        If False, the input value must be a single value.
    allow_na : bool
        If False, the input value cannot be None.
    allow_nan : bool
        If False, the input value cannot be NaN.
    allow_inf : bool
        If False, the input value cannot be infinite.

    Returns
    -------
    function
        A function that takes an input value and checks it against the set constraints.
        Returns an error message if the input value fails any of the constraints.
    """

    def inner(value: str):
        if not allow_multiple and len(value) != 1:
            return "Multiple values are not allowed."
        if not allow_na and value is None:
            return "NA values are not allowed."
        if not allow_nan and value == "NaN":
            return "NaN values are not allowed."
        if not allow_inf and value == "Inf":
            return "Infinite values are not allowed."

    return inner
