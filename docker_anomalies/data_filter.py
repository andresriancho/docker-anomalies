

class DataFilter():

    def __init__(self, name):
        """
        Initializes a DataFilter object. This object is responsible for
        deciding what to do with each item collected.
        """
        self.name = name
        self.rules = []
        self.actions = {}
        # FIXME: The user should be allowed to specify the default_action
        # (what to do when no rule is matched?). But due to a lack of time it
        # was hardcoded.
        self.default_action = "notify"

    def add_rule(self, rule):
        """
        Register a rule to the rule list.

        Arguments:
        ----------
        rule: A dictionary containing a rule definition.

        Note:
        -----
        The match conditions in the rule must be regexps and not strings.

        """
        self.rules.append(rule)

    def add_action(self, name, callback):
        """
        Register a callback for an action.

        Arguments:
        ----------
        - name: Identifies the callback when it has been referenced from a
          matching rule.
        - callback: A function to pass the item when it matches the conditions
          specified in the rule.
        """
        self.actions[name] = callback

    def filter(self, item):
        """
        Checks a item against each of the rules. Does the action of the first
        matching rule.

        """
        pass  # TODO
