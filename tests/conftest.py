import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


# set up tracing for tests
provider = TracerProvider()
test_exporter = InMemorySpanExporter()
provider.add_span_processor(SimpleSpanProcessor(test_exporter))
trace.set_tracer_provider(provider)


def get_trace():
    """Return all spans traced during this test."""
    return test_exporter.get_finished_spans()  # pragma: no cover


@pytest.fixture(autouse=True)
def clear_all_traces():
    test_exporter.clear()
