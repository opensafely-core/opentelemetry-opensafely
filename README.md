# opentelemetry-opensafely

[Opentelemetry](https://opentelemetry.io/) utils for OpenSAFELY.


Provides a function decorator [0] for instrumenting code with
OpenTelemetry traces.


## The @instrument decorator
The decorator allows you to skip much of the boilerplate involved in
setting up tracing spans. OpenTelemetry has a `@start_as_current_span`
decorator, but it doesn't allow adding custom attributes to it.

To use it:

### Basic use

```
from otel_opensafely.trace import instrument

@instrument
def my_function():
  ...
```
This automatically creates a span named "my_function". By default, the span is named after the function name. To use a custom name, pass a `span_name` argument.

### With named span
```
@instrument(span_name="my_span")
def my_function():
  ...
```
This creates a span named "my_function".


### With custom attributes

To add custom attributes to the span:

```
@instrument(span_name="my_span", "attributes": {"foo": "bar})
def my_function(foo, *, bar=None):
  ...
```

### With attributes from the function arguments

Sometimes we might want to add attributes that are based on the
value of a parameter, rather than static values. E.g. in the
function below, we want to add an attribute with the value of "name",
so we can filter traces by name.

```
def say_hello(*, nm):
  print(f"Hello {nm}")
```

To do this, use `kwarg_attributes`; a dict of k:v pairs, where
k is the name of the attribute to add, and v is the keyword argument:

```
@instrument(kwarg_attrbutes={"name": "nm"})
def say_hello(*, nm):
  print(f"Hello {nm}")
```

Calling this function with `say_hello(nm="Bob")` will add the attribute
`{"name": "Bob"}` to this span.

Positional arguments can be added as attributes in a similar way, using
`arg_attributes`; a dict of k:v pairs, in this case
k is the name of the attribute to add, and v is the index of the
positional argument to be use:

```
@instrument(arg_attrbutes={"name": 0})
def say_hello(nm):
  print(f"Hello {nm}")
```
Calling this function with `say_hello("Bob")` will add the attribute
`{"name": "Bob"}` to this span.

An `existing_tracer` can be passed to the decorator, if one has been
defined already; if not, a tracer is created, named with the `OTEL_SERVICE_NAME`
environment variable, if it exists, or the function module.


## Developer docs

Please see the [additional information](DEVELOPERS.md).


[0] Borrowed heavily from [this post](https://betterprogramming.pub/using-decorators-to-instrument-python-code-with-opentelemetry-traces-d7f1c7d6f632)
