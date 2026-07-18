class AnalyticsError(RuntimeError):
    """Base error for deterministic Intelligence analytics."""


class AnalyticsVerificationError(AnalyticsError):
    """An analytical output failed integrity verification."""
