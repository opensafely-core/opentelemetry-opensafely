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


def test_instrument_decorator_with_function_kwarg_attributes():
    @instrument(kwarg_attributes={"number": "num"})
    def assert_function_kwarg_attributes(*, num):
        current_span = trace.get_current_span()
        assert current_span.attributes == {"number": str(num)}

    assert_function_kwarg_attributes(num=1)


def test_instrument_decorator_with_function_arg_attributes():
    @instrument(arg_attributes={"number": 0})
    def assert_function_arg_attributes(num):
        current_span = trace.get_current_span()
        assert current_span.attributes == {"number": str(num)}

    assert_function_arg_attributes(1)


@pytest.mark.parametrize(
    "instrument_params,expect_ok",
    [
        ({"kwarg_attributes": {"number": "foo"}}, False),
        ({"arg_attributes": {"number": 1}}, False),
        ({"arg_attributes": {"number": 0}}, True),
    ],
)
def test_instrument_decorator_with_invalid_function_attributes(
    instrument_params, expect_ok
):
    @instrument(**instrument_params)
    def decorated_function(num):
        current_span = trace.get_current_span()
        assert current_span.attributes == {"number": str(num)}

    if expect_ok:
        decorated_function(1)
    else:
        with pytest.raises(AssertionError, match="not found in function signature"):
            decorated_function(1)
