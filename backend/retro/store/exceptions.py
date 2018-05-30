class NodeNotFoundError(Exception):
    pass


class NodeLockedError(Exception):
    pass


class LockFailureError(Exception):
    pass


class UnlockFailureError(Exception):
    pass


class UnknownEventError(Exception):
    pass
