"""
This module contains items related to translation between multiple languages.
Currently, it contains AlphabetDictionary, which is used with the encoder Cog,
and FormatDictionary, which is used with the logger Cog.
"""

from aenum import NamedConstant


class AlphabetDictionary(NamedConstant):
    """
    This Class contains NamedConstant dictionaries that list how one set of characters correlate to another.
    It is used by the encoder Cog to translate between certain character sets.
    """
    MORSE_TO_ALPHABET = {
        '• −': 'a',
        '− • • •': 'b',
        '− • − •': 'c',
        '− • •': 'd',
        '•': 'e',
        '• • − •': 'f',
        '− − •': 'g',
        '• • • •': 'h',
        '• •': 'i',
        '• − − −': 'j',
        '− • −': 'k',
        '• − • •': 'l',
        '− −': 'm',
        '− •': 'n',
        '− − −': 'o',
        '• − − •': 'p',
        '− − • −': 'q',
        '• − •': 'r',
        '• • •': 's',
        '−': 't',
        '• • −': 'u',
        '• • • −': 'v',
        '• − −': 'w',
        '− • • −': 'x',
        '− • − −': 'y',
        '− − • •': 'z',
        '− − − − −': '0',
        '• − − − −': '1',
        '• • − − −': '2',
        '• • • − −': '3',
        '• • • • −': '4',
        '• • • • •': '5',
        '− • • • •': '6',
        '− − • • •': '7',
        '− − − • •': '8',
        '− − − − •': '9',
        '• − • − • −': '.',
        '− − • • − −': ',',
        '− − − • • •': ':',
        '• • − − • •': '?',
        '• − − − − •': '\'',
        '− • • • • −': '-',
        '− • • − •': '/',
        '− • − − • −': '|',
        '• − • • − •': '\"',
        '• − − • − •': '@',
        '− • • • −': '=',
        '• • • • • • • •': '[ERROR]',
        '  /  ': ' '
    }
    ALPHABET_TO_MORSE = {
        'a': '• −',
        'b': '− • • •',
        'c': '− • − •',
        'd': '− • •',
        'e': '•',
        'f': '• • − •',
        'g': '− − •',
        'h': '• • • •',
        'i': '• •',
        'j': '• − − −',
        'k': '− • −',
        'l': '• − • •',
        'm': '− −',
        'n': '− •',
        'o': '− − −',
        'p': '• − − •',
        'q': '− − • −',
        'r': '• − •',
        's': '• • •',
        't': '−',
        'u': '• • −',
        'v': '• • • −',
        'w': '• − −',
        'x': '− • • −',
        'y': '− • − −',
        'z': '− − • •',
        '0': '− − − − −',
        '1': '• − − − −',
        '2': '• • − − −',
        '3': '• • • − −',
        '4': '• • • • −',
        '5': '• • • • •',
        '6': '− • • • •',
        '7': '− − • • •',
        '8': '− − − • •',
        '9': '− − − − •',
        '.': '• − • − • −',
        ',': '− − • • − −',
        ':': '− − − • • •',
        '?': '• • − − • •',
        '\'': '• − − − − •',
        '-': '− • • • • −',
        '/': '− • • − •',
        '(': '− • − − • −',
        ')': '− • − − • −',
        '[': '− • − − • −',
        ']': '− • − − • −',
        '{': '− • − − • −',
        '}': '− • − − • −',
        '\"': '• − • • − •',
        '@': '• − − • − •',
        '=': '− • • • −',
        '[ERROR]': '• • • • • • • •',
        ' ': '  /  '
    }


class FormatDictionary(NamedConstant):
    """
    This Class contains NamedConstant dictionaries that list how one set of characters correlate to another.
    It is used by the logger Cog to translate between certain formatting standards.
    """
    MARKDOWN_TO_RTF_GROUPS = {
        r'__': r'\\ul',             # underline
        r'~~': r'\\strike',         # strikethrough
        r'\*\*\*': r'\\b\\i',       # bold and italic
        r'\*\*': r'\\b',            # bold
        r'\*': r'\\i',              # italics 1
        r'_': r'\\i',               # italics 2
    }

    MARKDOWN_TO_RTF_CHARACTERS = {
        '\n': '\\line ',            # newline
        '\\*': r'{\'2a}',           # asterisk
        '\\_': r'{\'5f}',           # underscore
        # '{': r'{\'7b}',             # left curly brace; currently doesn't work
        # '}': r'{\'7c}',             # right curly brace; currently doesn't work
        '\\~': r'{\'7e}',           # tilde
        '\u2013': '\\endash',       # endash
        '\u2014': '\\emdash ',      # emdash
        '\u201C': '\\ldblquote ',   # left double quote
        '\u201D': '\\rdblquote ',   # right double quote
        '\u2018': '\\lquote ',      # left single quote
        '\u2019': '\\rquote ',      # right single quote
        '\u2026': r'{\'85}',        # ellipsis
        '\u00c0': r'{\'c0}',        # A with grave
        '\u00c1': r'{\'c1}',        # A with acute
        '\u00c2': r'{\'c2}',        # A with circumflex
        '\u00c3': r'{\'c3}',        # A with tilde
        '\u00c4': r'{\'c4}',        # A with diaeresis
        '\u00c5': r'{\'c5}',        # A with ring
        '\u00c6': r'{\'c6}',        # AE character
        '\u00c7': r'{\'c7}',        # C with cedilla
        '\u00c8': r'{\'c8}',        # E with grave
        '\u00c9': r'{\'c9}',        # E with acute
        '\u00ca': r'{\'ca}',        # E with circumflex
        '\u00cb': r'{\'cb}',        # E with diaeresis
        '\u00cc': r'{\'cc}',        # I with grave
        '\u00cd': r'{\'cd}',        # I with acute
        '\u00ce': r'{\'ce}',        # I with circumflex
        '\u00cf': r'{\'cf}',        # I with diaeresis
        '\u00d0': r'{\'d0}',        # Eth character
        '\u00d1': r'{\'d1}',        # N with tilde
        '\u00d2': r'{\'d2}',        # O with grave
        '\u00d3': r'{\'d3}',        # O with acute
        '\u00d4': r'{\'d4}',        # O with circumflex
        '\u00d5': r'{\'d5}',        # O with tilde
        '\u00d6': r'{\'d6}',        # O with diaeresis
        '\u00d7': r'{\'d7}',        # multiplication sign
        '\u00d8': r'{\'d8}',        # O with stroke
        '\u00d9': r'{\'d9}',        # U with grave
        '\u00da': r'{\'da}',        # U with acute
        '\u00db': r'{\'db}',        # U with circumflex
        '\u00dc': r'{\'dc}',        # U with diaeresis
        '\u00dd': r'{\'dd}',        # Y with acute
        '\u00de': r'{\'de}',        # upper thorn
        '\u00df': r'{\'df}',        # eszett
        '\u00e0': r'{\'e0}',        # a with grave
        '\u00e1': r'{\'e1}',        # a with acute
        '\u00e2': r'{\'e2}',        # a with circumflex
        '\u00e3': r'{\'e3}',        # a with tilde
        '\u00e4': r'{\'e4}',        # a with diaeresis
        '\u00e5': r'{\'e5}',        # a with ring
        '\u00e6': r'{\'e6}',        # ae character
        '\u00e7': r'{\'e7}',        # c with cedilla
        '\u00e8': r'{\'e8}',        # e with grave
        '\u00e9': r'{\'e9}',        # e with acute
        '\u00ea': r'{\'ea}',        # e with circumflex
        '\u00eb': r'{\'eb}',        # e with diaeresis
        '\u00ec': r'{\'ec}',        # i with grave
        '\u00ed': r'{\'ed}',        # i with acute
        '\u00ee': r'{\'ee}',        # i with circumflex
        '\u00ef': r'{\'ef}',        # i with diaeresis
        '\u00f0': r'{\'f0}',        # eth character
        '\u00f1': r'{\'f1}',        # n with tilde
        '\u00f2': r'{\'f2}',        # o with grave
        '\u00f3': r'{\'f3}',        # o with acute
        '\u00f4': r'{\'f4}',        # o with circumflex
        '\u00f5': r'{\'f5}',        # o with tilde
        '\u00f6': r'{\'f6}',        # o with diaeresis
        '\u00f7': r'{\'f7}',        # division sign
        '\u00f8': r'{\'f8}',        # o with stroke
        '\u00f9': r'{\'f9}',        # u with grave
        '\u00fa': r'{\'fa}',        # u with acute
        '\u00fb': r'{\'fb}',        # u with circumflex
        '\u00fc': r'{\'fc}',        # u with diaeresis
        '\u00fd': r'{\'fd}',        # y with acute
        '\u00fe': r'{\'fe}',        # lower thorn
        '\u00ff': r'{\'ff}',        # y with diaeresis
    }
