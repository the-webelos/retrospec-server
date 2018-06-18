from .exceptions import UnsupportedOperationError


class OperationFactory(object):
    valid_ops = ["SET", "INCR", "DELETE"]

    def build_operation(self, op, field, value):
        if op == "SET":
            return SetOperation(field, value)
        elif op == "INCR":
            return IncrementOperation(field, value)
        elif op == "DELETE":
            return DeleteOperation(field)
        else:
            raise UnsupportedOperationError("Unsupported operation type '%s'! Must be one of %s." % (op, self.valid_ops))


class BaseOperation(object):
    def execute(self, node):
        raise NotImplementedError("Subclass must implement 'execute'!")


class SetOperation(BaseOperation):
    def __init__(self, field, value):
        super(SetOperation, self).__init__()
        self.field = field
        self.value = value

    def execute(self, node):
        node.content[self.field] = self.value


class IncrementOperation(BaseOperation):
    def __init__(self, field, value):
        super(IncrementOperation, self).__init__()
        self.field = field
        self.value = value

    def execute(self, node):
        node.content[self.field] = int(node.content.get(self.field, 0)) + int(self.value)


class DeleteOperation(BaseOperation):
    def __init__(self, field):
        super(DeleteOperation, self).__init__()
        self.field = field

    def execute(self, node):
        node.content.pop(self.field, None)
