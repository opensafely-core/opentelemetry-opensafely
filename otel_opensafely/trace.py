from functools import wraps
from inspect import Parameter, signature
from os import environ
from typing import Dict

from opentelemetry import trace


def instrument(
    _func=None,
    *,
    span_name: str = "",
    record_exception: bool = True,
    attributes: Dict[str, str] = None,
    func_attributes: Dict[str, str] = None,
    existing_tracer: trace.Tracer = None,
):
    """
    A decorator to instrument a function with an OTEL tracing span.

    span_name: custom name for the span, defaults to name of decorated function
    record_exception: passed to `start_as_current_span`; whether to record
      exceptions when they happen.
    attributes: custom attributes to set on the span
    func_attributes: k, v pairs of attribute name to function parameter
      name. Sets the span attribute k to the str representation of
      the function argument v (can be either positional or keyword argument).
      v must be either a string, or an object that can be passed to str().
    existing_tracer: pass an optional existing tracer to use. Defaults to
      a tracer named with the value of the environment variable
      `OTEL_SERVICE_NAME` if available, or the name of the module containing
      the decoraated function.
    """

    def span_decorator(func):
        tracer = existing_tracer or trace.get_tracer(
            environ.get("OTEL_SERVICE_NAME", func.__module__)
        )
        name = span_name or func.__qualname__
        attributes_dict = attributes or {}
        func_signature = signature(func)
        default_params = {
            param_name: param.default
            for param_name, param in func_signature.parameters.items()
            if param and param.default is not Parameter.empty
        }

        @wraps(func)
        def wrap_with_span(*args, **kwargs):
            if func_attributes is not None:
                bound_args = func_signature.bind(*args, **kwargs).arguments
                for attribute, parameter_name in func_attributes.items():
                    # Find the value of this parameter by(in order):
                    # 1) the function kwargs directly; if a function signature takes a parameter
                    # like `**kwargs`, we can retrieve a named parameter from the keyword arguments
                    # there
                    # 2) the bound args retrieved from the function signature; this will find any
                    # explicity passed values when the function was called.
                    # 3) the parameter default value, if there is one
                    # 4) Finally, raises an exception if we can't find a value for the expected parameter
                    if parameter_name in kwargs:
                        func_arg = kwargs[parameter_name]
                    elif parameter_name in bound_args:
                        func_arg = bound_args[parameter_name]
                    elif parameter_name in default_params:
                        func_arg = default_params[parameter_name]
                    else:
                        raise AttributeError(
                            f"Expected argument {parameter_name} not found in function signature"
                        )
                    attributes_dict[attribute] = str(func_arg)

            with tracer.start_as_current_span(
                name, record_exception=record_exception, attributes=attributes_dict
            ):
                return func(*args, **kwargs)

        return wrap_with_span

    if _func is None:
        return span_decorator
    else:
        return span_decorator(_func)
