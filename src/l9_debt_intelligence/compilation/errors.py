class CompilationError(RuntimeError):
    """Base error for prevention candidate compilation."""


class CompilationVerificationError(CompilationError):
    """Compiled candidate artifacts failed verification."""
