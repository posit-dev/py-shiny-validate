from typing import Callable

err_msg_zero_length_value = "Must not contain zero values."
err_msg_allow_multiple = "Must not contain multiple values."
err_msg_allow_none = "Value must not be 'None'"
err_msg_allow_infinite = "Must not contain infinite values."


def check_input_length(
    input: any,
    input_name: str,
    stop_message: str = "The input for `{input_name}` must contain values.",
):
    if len(input) < 1:
        stop_message = stop_message.format(input_name=input_name)
        raise ValueError(stop_message)


def input_provided(val: any):
    print(val)
    if val is None:
        return False
    if isinstance(val, Exception):
        return False
    return True


def required(message: str = "Required", test: Callable = input_provided):
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


def optional(test: Callable = input_provided):
    """
    Generate a validation function that indicates an input is allowed to not be present.
    If an optional rule sees that an input is not present, subsequent rules for that input are skipped and the input is considered valid.
    Otherwise, the rule simply passes. optional will never return a validation error/message.

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


def regex(pattern: str, message: str, ignore_case: bool = False):
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


def email(
    message: str = "Not a valid email address",
    allow_multiple: bool = False,
    allow_none: bool = False,
):
    """
    Generate a validation function that checks if the input value is a valid email address.

    Parameters
    ----------
    message : str
        The error message to return if the input value is not a valid email address.
    allow_multiple : bool, optional
        If True, multiple email addresses are allowed. Default is False.
    allow_none : bool, optional
        If True, None values are allowed. Default is False.

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

        if allow_none and value is None:
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


def url(
    message: str = "Not a valid URL",
    allow_multiple: bool = False,
    allow_none: bool = False,
):
    """
    Generate a validation function that checks if the input value is a valid URL.

    Parameters
    ----------
    message : str
        The error message to return if the input value is not a valid URL.
    allow_multiple : bool, optional
        If True, multiple URLs are allowed. Default is False.
    allow_none : bool, optional
        If True, None values are allowed. Default is False.

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

        if allow_none and value is None:
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


def basic(allow_multiple: bool, allow_none: bool, allow_nan: bool, allow_inf: bool):
    """
    Basic validation function.

    Parameters
    ----------
    allow_multiple : bool
        If False, the input value must be a single value.
    allow_none : bool
        If False, the input value cannot be None.
    allow_inf : bool
        If False, the input value cannot be infinite.

    Returns
    -------
    function
        A function that takes an input value and checks it against the set constraints.
        Returns an error message if the input value fails any of the constraints.
    """

    def inner(value: str):
        if not allow_none and value is None:
            return "NA values are not allowed."
        if not allow_inf and value == "Inf":
            return "Infinite values are not allowed."

    return inner


def check_none(value, allow_none):
    if allow_none and value is None:
        err_msg_allow_none


def integer(
    message: str = "An integer is required",
    allow_none: bool = False,
):
    """
    Generate a validation function that checks if the input value is an integer.

    Parameters
    ----------
    message : str
        The error message to return if the input value is not an integer.
    allow_none:
        If False, the input value cannot be None.

    Returns
    -------
    function
        A function that takes an input value and returns the error message if the input value is not an integer.
    """

    def inner(value: str):
        if len(value) == 0:
            return err_msg_zero_length_value

        if not allow_none and value is None:
            return err_msg_allow_none

        if not isinstance(value, int):
            return message

    return inner


def between(
    left: float,
    right: float,
    inclusive: list[bool],
    message_fmt: str = "Must be between {left} and {right}.",
    allow_none: bool = False,
):
    message = message_fmt.format(left=left, right=right)

    def inner(value):
        if allow_none:
            if left is None:
                return err_msg_allow_none
            if right is None:
                return err_msg_allow_none

        if inclusive[0]:
            l_of_left = value < left
        else:
            l_of_left = value <= left

        if inclusive[1]:
            l_or_right = value > right
        else:
            l_or_right = value >= right

        if l_of_left or l_or_right:
            return message

    return inner


def prepare_values_text(set: set, limit: int) -> str:
    if limit is not None and len(set) > limit:
        num_omitted = len(set) - limit

        values_str = ", ".join(str(i) for i in list(set)[:limit])

        additional_text = f"(and {num_omitted} more)"

        values_str = f"{values_str} {additional_text}"
    else:
        values_str = ", ".join(str(i) for i in set)

    return values_str


def in_set(
    set: set, message_fmt: str = "Must be in the set of {values_text}.", set_limit=3
):
    values_text = prepare_values_text(set, limit=set_limit)

    message = message_fmt.format(values_text=values_text)

    def inner(value):
        if value not in set:
            return message

    return inner


def compare(
    rhs: float,
    message_fmt: str,
    operator: Callable,
    allow_none: bool = False,
):
    # Preparation of the message
    message = message_fmt.format(rhs=rhs)

    # Testing of `value` and validation
    def inner(value):
        if not allow_none and value is None:
            return err_msg_allow_none

        res = operator(value, rhs)

        if not res:
            return message.format(rhs=rhs)

    return inner


def gt(rhs: float, allow_none: bool = False, message_fmt="Must be greater than {rhs}."):
    def inner(value):
        compare(
            rhs=rhs,
            message_fmt=message_fmt,
            allow_none=allow_none,
            operator=lambda value, rhs: value > rhs,
        )

    return inner


def gte(
    rhs: float,
    allow_none: bool = False,
    message_fmt="Must be greater than or equal to {rhs}.",
):
    def inner(value):
        compare(
            rhs=rhs,
            message_fmt=message_fmt,
            allow_none=allow_none,
            operator=lambda value, rhs: value >= rhs,
        )

    return inner


def lt(rhs: float, allow_none: bool = False, message_fmt="Must be less than {rhs}."):
    def inner(value):
        compare(
            rhs=rhs,
            message_fmt=message_fmt,
            allow_none=allow_none,
            operator=lambda value, rhs: value < rhs,
        )

    return inner


def lte(
    rhs: float,
    allow_none: bool = False,
    message_fmt="Must be less than or equal to {rhs}.",
):
    def inner(value):
        compare(
            rhs=rhs,
            message_fmt=message_fmt,
            allow_none=allow_none,
            operator=lambda value, rhs: value <= rhs,
        )

    return inner


def equal(rhs: float, allow_none: bool = False, message_fmt="Must be equal to {rhs}."):
    def inner(value):
        compare(
            rhs=rhs,
            message_fmt=message_fmt,
            allow_none=allow_none,
            operator=lambda value, rhs: value == rhs,
        )

    return inner


def not_equal(
    rhs: float, allow_none: bool = False, message_fmt="Must not be equal to {rhs}."
):
    def inner(value):
        compare(
            rhs=rhs,
            message_fmt=message_fmt,
            allow_none=allow_none,
            operator=lambda value, rhs: value != rhs,
        )

    return inner
