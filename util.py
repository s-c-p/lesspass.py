from collections.abc import Mapping as dictType

def get_target_dct(dct, locations):
    if len(locations) > 1:
        k, *remaining = locations
        return get_target_dct(dct[k], remaining)
    else:
        return dct[locations.pop()]

class UpdateDict:
    def __init__(self, master_dict):
        self.dct = {k: v for k, v in master_dict.items()}
        self.dct_map = dict()
        self.ambigious = list()
        self._ctx_tracker = list()
        self._scan(self.dct, self._ctx_tracker)
        return

    def _scan(self, dct, ctx):
        """
given = {
    'a': 0,
    'b': 1,
    'c': {
        'p': 0,
        'q': 1,
        'r': {
            'x': 0,
            'y': 1,
            'z': {'a': None}
        }
    }
}

expected = {
    'a' : ['c', 'r', 'z'],
    'b' : [],
    'c' : [],
    'p' : ['c'],
    'q' : ['c'],
    'r' : ['c'],
    'x' : ['c', 'r'],
    'y' : ['c', 'r'],
    'z' : ['c', 'r']
}

        """
        for k, v in dct.items():
            if k in self.dct_map:
                self.ambigious.append(k)
                print('warning', k)
            self.dct_map[k] = ctx
            if isinstance(v, dictType):
                ctx.append(k)
                new_ctx = ctx[:]
                self._scan(v, new_ctx)
                ctx.pop()
        return

    def _update(self, *keys_and_val):
        """
>>> l = dict(zip(list('abc'), range(3)))
>>> l['b'] = dict(zip(list('abc'), range(3)))
>>> l['b']['c'] = dict(zip(list('abc'), range(3)))
>>> l['b']['c']['a'] = 100
(b, c, a, 100)
        """
        if len(xxx) < 2:
            raise NotEnoughInfo
        value, *location = xxx[::-1]
        location.reverse()
        final_key = location.pop()
        ptr__target_dct = get_target_dct(location)
        ptr__target_dct[final_key] = value
        return

    def with_list(self, *args):
        if isinstance(args, list):
            for an_update in args:
                self._update(an_update)
        else:
            self._update(args)
        return self.dct

    def with_dict(self, u):
        for k, v in u.items()
