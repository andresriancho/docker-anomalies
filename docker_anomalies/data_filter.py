

class DataFilter():

    def __init__(self, name):
        self.name = name
        self.rules = []
        self.actions = {}

    def add_rule(self, rule):
        """
        Register a rule to the rule list.
        """
        self.rules.append(rule)

    def add_action(self, name, callback):
        """
        Register a callback for an action.
        """
        self.actions[name] = callback

    def filter(self, item):
        """
        Checks a item against each of the rules. Does the action of the first
        matching rule.
        """
        pass  # TODO
