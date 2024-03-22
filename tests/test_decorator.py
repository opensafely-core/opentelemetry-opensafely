import pytest
from opentelemetry import trace

from otel_opensafely.trace import instrument


def test_not_instrument_decorator():
    assert trace.get_current_span().is_recording() is False


@instrument
def test_instrument_decorator():
    current_span = trace.get_current_span()
    assert current_span.is_recording() is True
    assert current_span.name == "test_instrument_decorator"


@instrument(span_name="testing", attributes={"foo": "bar"})
def test_instrument_decorator_with_name_and_attributes():
    current_span = trace.get_current_span()
    assert current_span.is_recording() is True
    assert current_span.name == "testing"
    assert current_span.attributes == {"foo": "bar"}


@pytest.mark.parametrize(
    "func_attributes,func_args,func_kwargs,expected_attributes",
    [
        # positional arg
        ({"func_attributes": {"number": "num"}}, (1,), {}, {"number": "1"}),
        # keyword arg
        (
            {"func_attributes": {"text": "string"}},
            (1,),
            {"string": "bar"},
            {"text": "bar"},
        ),
        # default keyword arg
        ({"func_attributes": {"text": "string"}}, (1,), {}, {"text": "Foo"}),
        # all args passed as keywords
        (
            {"func_attributes": {"number": "num"}},
            (),
            {"num": 1, "string": "bar"},
            {"number": "1"},
        ),
        # all args passed as positional
        ({"func_attributes": {"number": "num"}}, (1, "bar"), {}, {"number": "1"}),
        # multiple func attributes
        (
            {"func_attributes": {"number": "num", "text": "string"}},
            (1,),
            {},
            {"number": "1", "text": "Foo"},
        ),
    ],
)
def test_instrument_decorator_with_function_attributes(
    func_attributes, func_args, func_kwargs, expected_attributes
):
    @instrument(**func_attributes)
    def assert_function_kwarg_attributes(num, string="Foo"):
        current_span = trace.get_current_span()
        assert current_span.attributes == expected_attributes
        return num, string

    assert_function_kwarg_attributes(*func_args, **func_kwargs)


@pytest.mark.parametrize(
    "func_kwargs,expect_ok",
    [
        ({}, False),
        ({"foo": 1}, False),
        ({"bar": 1}, True),
    ],
)
def test_instrument_decorator_with_unnamed_kwargs(func_kwargs, expect_ok):
    @instrument(func_attributes={"foo": "bar"})
    def decorated_function(**kwargs):
        current_span = trace.get_current_span()
        assert current_span.attributes == {"foo": str(kwargs["bar"])}

    if expect_ok:
        decorated_function(**func_kwargs)
    else:
        with pytest.raises(AttributeError, match="not found in function signature"):
            decorated_function(**func_kwargs)
