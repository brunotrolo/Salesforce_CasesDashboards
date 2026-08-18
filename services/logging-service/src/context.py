import contextvars


class RequestContext:
    """Async-safe per-request context (trace_id/correlation_id)."""

    _trace_id: contextvars.ContextVar = contextvars.ContextVar(
        "trace_id", default=None
    )
    _correlation_id: contextvars.ContextVar = contextvars.ContextVar(
        "correlation_id", default=None
    )

    @classmethod
    def set_trace_id(cls, trace_id: str) -> None:
        cls._trace_id.set(trace_id)

    @classmethod
    def get_trace_id(cls) -> str:
        return cls._trace_id.get()

    @classmethod
    def set_correlation_id(cls, correlation_id: str) -> None:
        cls._correlation_id.set(correlation_id)

    @classmethod
    def get_correlation_id(cls) -> str:
        return cls._correlation_id.get()

    @classmethod
    def clear(cls) -> None:
        cls._trace_id.set(None)
        cls._correlation_id.set(None)