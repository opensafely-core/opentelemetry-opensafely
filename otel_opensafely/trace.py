from functools import wraps
from os import environ
from typing import Dict

from opentelemetry import trace


def instrument(
    _func=None,
    *,
    span_name: str = "",
    record_exception: bool = True,
    attributes: Dict[str, str] = None,
    arg_attributes: Dict[str, int] = None,
    kwarg_attributes: Dict[str, str] = None,
    existing_tracer: trace.Tracer = None,
):
    """
    A decorator to instrument a function with an OTEL tracing span.
    attributes: custom attributes to set on the span
    arg_attributes: k, v pairs of attribute name to index of positional
       arg. Sets the span attribute k to the str representation of the
       the arg at index v
    kwarg_attributes: k, v pairs of attribute name to function
       kwarg. Sets the span attribute k to the str representation of
       the function kwarg v
    """

    def span_decorator(func):
        tracer = existing_tracer or trace.get_tracer(
            environ.get("OTEL_SERVICE_NAME", func.__module__)
        )

        def _set_attributes(span, attributes_dict):
            for att in attributes_dict:
                span.set_attribute(att, attributes_dict[att])

        @wraps(func)
        def wrap_with_span(*args, **kwargs):
            name = span_name or func.__qualname__
            with tracer.start_as_current_span(
                name, record_exception=record_exception
            ) as span:
                attributes_dict = attributes or {}
                if kwarg_attributes is not None:
                    for k, v in kwarg_attributes.items():
                        assert (
                            v in kwargs
                        ), f"Expected kwarg {v} not found in function signature"
                        attributes_dict[k] = str(kwargs[v])

                if arg_attributes is not None:
                    for k, v in arg_attributes.items():
                        assert (
                            len(args) > v
                        ), f"Expected positional arg at index {v} not found in function signature"
                        attributes_dict[k] = str(args[v])

                _set_attributes(span, attributes_dict)
                return func(*args, **kwargs)

        return wrap_with_span

    if _func is None:
        return span_decorator
    else:
        return span_decorator(_func)
