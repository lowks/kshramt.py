import sys
import argparse
import unittest
import collections
import pprint


__version__ = '0.0.3'


class Error(Exception):
    pass


def pp(x):
    pprint.pprint(x, stream=sys.stderr)
    return x


def flatten(xss):
    """
    # Flatten containers

    ## Note
    Do not include recursive elements.

    ## Exceptions
    - `RuntimeError`: Recursive elements will cause this
    """
    if isinstance(xss, str):
        yield xss
    else:
        for xs in xss:
            if isinstance(xs, collections.Iterable):
                for x in flatten(xs):
                    yield x
            else:
                yield xs


def list_2d(n_row, n_column):
    assert n_row >= 1
    assert n_column >= 1

    return [[None
             for _
             in range(n_column)]
            for _
            in range(n_row)]


def make_fixed_format_parser(fields):
    """
    fields: [{'name': 'density', 'converter': int,   'length': 3},
             {'name': 'opacity', 'converter': float, 'length': 7}]
    """
    lower = 0
    _fields = []
    for field in fields:
        assert field['length'] >= 1
        _field = {k: v for k, v in field.items()}
        upper = lower + field['length']
        _field['lower'] = lower
        _field['upper'] = upper
        lower = upper
        _fields.append(_field)

    def fixed_format_parser(s):
        assert len(s) >= upper
        ret = {}
        for field in _fields:
            name = field['name']
            f = field['converter']
            l = field['lower']
            u = field['upper']
            ret[name] = f(s[l:u])
        return ret
    return fixed_format_parser


class TestAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super().__init__(option_strings=option_strings,
                         dest=dest,
                         default=default,
                         nargs=0,
                         help=help)


    def __call__(self, parser, namespace, values, option_string=None):
        unittest.main(argv=sys.argv[:1])
        parser.exit()


class Tester(unittest.TestCase):
    def test_list_2d(self):
        self.assertEqual(list_2d(2, 3),
                         [[None, None, None],
                          [None, None, None]])

    def test_flatten(self):
        self.assertEqual(list(flatten([])), [])
        self.assertEqual(list(flatten([1, 2])), [1, 2])
        self.assertEqual(list(flatten([1, [2, 3]])), [1, 2, 3])
        self.assertEqual(list(flatten(['ab'])), ['ab'])
        self.assertEqual(tuple(sorted(flatten((1, 2, (3, [4, set([5, 6]), 7 ], [8, 9]))))),
                         tuple(sorted((1, 2, 3, 4, 5, 6, 7, 8, 9))))

    def test_make_fixed_format_parser(self):
        with self.assertRaises(AssertionError):
            make_fixed_format_parser([{'name': 'a',
                                       'converter': int,
                                       'length': 0}])
        fixed_format_parser\
            = make_fixed_format_parser([{'name': 'a',
                                         'converter': int,
                                         'length': 3},
                                        {'name': 'b',
                                         'converter': lambda x: -int(x),
                                         'length': 7}])
        self.assertEqual(fixed_format_parser(' 325      '),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser(' 325      \n'),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser(' 32  5    '),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser('32   5    abc'),
                         {'a': 32, 'b': -5})
        with self.assertRaises(AssertionError):
            fixed_format_parser('123456789')


if __name__ == '__main__':
    unittest.main()
