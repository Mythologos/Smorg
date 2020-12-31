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
    MARKDOWN_TO_RTF = {
        r'__': r'\\ul',             # underline
        r'~~': r'\\strike',         # strikethrough
        r'\*\*\*': r'\\b\\i',       # bold and italic
        r'\*\*': r'\\b',            # bold
        r'\*': r'\\i',              # italics 1
        r'_': r'\\i',               # italics 2
    }
