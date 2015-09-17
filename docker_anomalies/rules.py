
import re



class Rules():
    
    ruleset = {'events': []}
    
    
    def __init__(self, rules):
        '''Parse a dict of rules'''
        
        for r in rules:
            target = r.pop('target')
            r['match'] = self._compile_regex(r['match'])
            self.ruleset[target].append(r)
            
    
    def _compile_regex(self, match):

        for key in match:
            match[key] = re.compile(match[key])
        return match
