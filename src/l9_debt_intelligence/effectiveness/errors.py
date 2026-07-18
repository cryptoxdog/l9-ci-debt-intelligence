class EffectivenessError(RuntimeError):
    """Base effectiveness measurement failure."""


class OutcomeValidationError(EffectivenessError):
    """An outcome event violates the effectiveness contract."""


class EffectivenessVerificationError(EffectivenessError):
    """An effectiveness artifact failed integrity verification."""
