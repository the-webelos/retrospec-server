class NodeNotFoundError(Exception):
    pass


class NodeParseError(Exception):
    pass


class NodeLockedError(Exception):
    pass


class LockFailureError(Exception):
    pass


class UnlockFailureError(Exception):
    pass


class ExistingNodeError(Exception):
    pass
