from __future__ import annotations


class ContractError(ValueError):
    """Base error for corpus contract failures."""


class SchemaValidationError(ContractError):
    """The event does not satisfy the corpus event schema."""


class ProducerCompatibilityError(ContractError):
    """The producer or producer contract is not supported."""


class SDKCompatibilityError(ContractError):
    """The event references an incompatible SDK contract."""
