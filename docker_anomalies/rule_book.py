import re
import sys
import yaml


from data_filter import DataFilter


class RuleBook():

    def __init__(self, path):
        '''
        Constructor for the RuleBook class.

        Returns:
        --------
        A dict of DataFilter objects loaded with the user-specified rules.
        '''
        raw_rulebook = self._open_rulebook_file(path)
        # Now parse every rule-set in the raw_rulebook
        filters = {}
        for ruleset_name in raw_rulebook:
            # Make a filter from the raw_ruleset taken from the rulebook.
            raw_ruleset = raw_rulebook[ruleset_name]
            filters[ruleset_name] = self._parse_raw_ruleset(ruleset_name,
                                                            raw_ruleset)
        return filters

    def _open_rulebook_file(self, path):
        '''
        Wrapper for file opening and IOError handling.
        '''
        try:
            raw_rulebook = yaml.load(open(path))
        except IOError:
            # TODO -> Wrap it arround the log_handler
            sys.stderr.write(IOError)
            exit(1)
        return raw_rulebook

    def _parse_raw_ruleset(self, name, raw_ruleset):
        '''
        Take a raw ruleset and return a DataFilter instance.

        Arguments:
        ----------
        - name: The name of the rule. (A description).
        - raw_ruleset: A list of unparsed rules specified by the user for this
          filter.

        Returns:
        --------
        Returns a DataFilter object containing the rules specified in the user
        defined rulebook.

        Note:
        -----
        The returned DataFilter object has none registered callbacks for the
        actions. They must be provided by the event consumers.

        '''
        data_filter = DataFilter(name)
        # Register the rules one by one:
        for raw_rule in raw_ruleset:
            raw_rule['match'] = self._compile_regexps(raw_ruleset['match'])
            data_filter.add_rule(raw_rule)
        return data_filter

    def _compile_regexps(raw_match_conditions):
        '''
        Take a dict of "raw" match conditions and compile them into python
        regular expressions.

        Arguments:
        ----------

        raw_match_conditions: A dictionary of match conditions taken from the
        raw_rulebook. The keys correspond to fields in the collected data and
        values are strings that can be compiled to python regular expressions.
        '''
        regexps = {}
        for field in raw_match_conditions:
            # Compile each of the user-specified match-conditions
            regexps[field] = re.compile(raw_match_conditions[field])
        return regexps
