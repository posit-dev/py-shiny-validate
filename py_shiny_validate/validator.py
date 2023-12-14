from shiny import reactive, ui, Session
from shiny.session import session_context
from .deps import html_deps
from typing import Optional, Callable
import datetime
from shiny.session import get_current_session, require_active_session


class Rule:
    def __init__(
        self,
        rule: Callable,
        label: str,
        session: Session,
    ):
        self.rule: Callable = rule
        self.label: str = label
        self.session: Session = session


class SkipValidation:
    def __init__(self):
        pass


class InputValidator:
    def __init__(
        self,
        priority=1000,
    ):
        self.__session = require_active_session(get_current_session())
        self.__priority: int = priority
        self.__condition = reactive.Value(None)
        self.__rules: reactive.Value[dict[str, Rule]] = reactive.Value({})

        self.__enabled: bool = False
        self.__observer_handle: Optional[reactive.Effect] = None
        self.__is_child = False
        self.__validator_infos: reactive.Value[
            dict[str, InputValidator]
        ] = reactive.Value({})

        ui.insert_ui(
            html_deps,
            "body",
            "beforeEnd",
            immediate=True,
            session=self.__session,
        )

    def parent(self, validator):
        self.disable()
        self.__is_child = True

    def condition(self, cond: Optional[Callable] = None):
        if cond is None:
            return self.__condition
        else:
            if not callable(cond) and cond is not None:
                raise ValueError("`cond` argument must be a formula or None")
            self.__condition = cond

    def add_validator(
        self,
        validator,
        label: Optional[str] = None,
    ):
        if not isinstance(validator, InputValidator):
            raise ValueError(
                "`validator` argument must be an instance of InputValidator"
            )
        label = label or str(validator)
        validator.parent(self)

        with reactive.isolate():
            validators = self.__validator_infos.get()
            validators[label] = validator
            self.__validator_infos.set(validators)

    def add_rule(self, inputId: str, rule: Callable):
        label = str(rule)
        if not callable(rule):
            raise ValueError("`rule` argument must be a function")

        with reactive.isolate():
            new_rules = self.__rules.get()
            new_rules[inputId] = Rule(rule, label, session=get_current_session())
            self.__rules.set(new_rules)

    def enable(self):
        if self.__is_child:
            return
        if not self.__enabled:
            with session_context(self.__session):

                @reactive.Effect(priority=self.__priority)
                async def observer():
                    results = self.validate()
                    await self.__session.send_custom_message(
                        "validation-jcheng5", results
                    )

                self.__enabled = True
                self.__observer_handle = observer
                return observer

    def disable(self):
        if self.__enabled:
            self.__observer_handle.destroy()
            self.__observer_handle = None
            self.__enabled = False
            if not self.__is_child:
                results = self.validate()
                results = {k: None for k in results}
                self.__session.send_custom_message("validation-jcheng5", results)

    def fields(self):
        return list(self.__rules().keys())

    def is_valid(self):
        results = self.validate()
        return all(result is None for result in results.values())

    def validate(self):
        result = self.__validate_impl()
        return result

    def __validate_impl(self):
        condition = self.__condition
        skip_all = callable(condition()) and condition() is not None

        if skip_all:
            fields = self.fields()
            return {field: None for field in fields}

        dependency_results = {}

        for validator_info in self.__validator_infos().values():
            child_results = validator_info.__validate_impl()
            dependency_results = {**dependency_results, **child_results}

        results = {}
        for name, rule in self.__rules().items():
            fullname = rule.session.ns(name)

            try:
                result = rule.rule(rule.session.input[name]())
            except Exception as e:
                result = "An unexpected error occurred during input validation: " + str(
                    e
                )

            result_is_html = isinstance(result, (str, bytes))
            if result_is_html:
                result = str(result)

            is_valid_result = (
                result is None
                or (isinstance(result, str))
                or result == SkipValidation()
            )

            if not is_valid_result:
                raise ValueError(
                    "Result of '"
                    + name
                    + "' validation was not a single-character vector (actual class: "
                    + str(type(result))
                    + ")"
                )

            if result is None:
                if fullname not in results:
                    results[fullname] = None
            elif result == SkipValidation():
                results[fullname] = True
            else:
                results[fullname] = {
                    "type": "error",
                    "message": result,
                    "is_html": result_is_html,
                }

        for key in results:
            if results[key] is True:
                results[key] = None

        return {**dependency_results, **results}


def merge_results(self, resultsA: dict, resultsB: dict) -> dict:
    results = {**resultsA, **resultsB}
    has_error = {k: v is not None for k, v in results.items()}
    results = {
        k: results[k] for k in sorted(has_error, key=has_error.get, reverse=True)
    }
    results = {
        k: v
        for k, v in results.items()
        if k not in list(results.keys())[list(results.values()).index(None) :]
    }
    return results


def input_provided(val):
    if val is None:
        return False
    if isinstance(val, Exception):
        return False
    if not isinstance(val, (int, float, str, bool)):
        return True
    if len(val) == 0:
        return False
    if all(v is None for v in val):
        return False
    return True


def timestamp_str(time=datetime.datetime.now()):
    return time.strftime("%Y-%m-%d %H:%M:%S.%f")
