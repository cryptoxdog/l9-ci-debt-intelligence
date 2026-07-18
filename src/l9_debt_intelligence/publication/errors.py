class PublicationError(RuntimeError):
    """Base defense-pack publication failure."""


class PublicationGateError(PublicationError):
    """A required publication gate did not pass."""


class SignatureVerificationError(PublicationError):
    """A detached defense-pack signature is invalid."""


class PublicationVerificationError(PublicationError):
    """Published defense-pack integrity verification failed."""
