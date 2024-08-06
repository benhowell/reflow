# def compute_args_error(n):
#     return """
#            ERROR: compute_fn takes either one or two arguments only
#                   first argument must be the input flowing from signal_fn
#                   second argument is the query vector: qry_v (if required)
#                   arguments given: {x}""".format(x=n)



# def signal_args_error(n):
#     return """
#            ERROR: signal_fn takes either zero or one argument only
#                   the argument is the query vector: qry_v (if required)
#                   arguments given: {x}""".format(x=n)



class SubscribeArgumentError(Exception):
    """
    Raised when arguments supplied to subscribe are incorrect.
    """
    def __init__(self):
        self.message = """ERROR: Arguments passed to subscribe are incorrect."""
        super().__init__(self.message)


class GraphCycleError(Exception):
    """
    Raised when graph contains cycles.
    """
    def __init__(self):
        self.message = """ERROR: failed to create node graph. Subscription/flow graph contains cycles. Ensure your subscriptions and/or flows contain no circular references."""
        super().__init__(self.message)



class FlowArgumentError(Exception):
    """
    Raised when arguments in a flow are found to be invalid.
    """
    def __init__(self, id, kind):
        self.id = id
        if kind == 'id':
            self.message = 'Flows require an "id" value'
        elif kind == 'inputs':
            self.message = 'Flows require an "inputs" map to specify one or more "path" or "flow" inputs'
        elif kind == 'input_args':
            self.message = 'Flow inputs need to include at least one path or one flow'
        elif kind == 'output':
            self.message = 'Flows require an "output" function'
        else:
            self.message = 'Unknown error'
        self.message = '[Flow ' + str(id) + ']: ' + self.message
        super().__init__(self.message)



class DictTypeError(Exception):
    """
    Raised when an object cannot be validated as a is dict/map type
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)




#FIXME:
#print("No subscription handler registered for: ".format(x=id))
