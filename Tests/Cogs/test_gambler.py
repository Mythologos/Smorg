# TODO: will contain tests for the Gambler Cog and its composite commands

import pytest
from ...Bot.Cogs.gambler import Gambler


class TestRoll:
    @staticmethod
    @pytest.mark.asyncio()
    @pytest.mark.parametrize('roll, result',
                             [("1d6", [('1d6', '', '', '', '')]),
                              ("1d6+2", [('1d6', '', '', '', ''), ('', '+', '', '', ''), ('', '', '', '', '2')]),
                              ("10d6d1", [('10d6d1', '', '', '', '')]),
                              ("10d6k1", [('10d6k1', '', '', '', '')]),
                              ("10d6!", [('10d6!', '', '', '', '')]),
                              ("1d6<3", [('1d6<3', '', '', '', '')]),
                              ("1d6>3", [('1d6>3', '', '', '', '')]),
                              ("10d10k5!<5+1", [('10d10k5!<5', '', '', '', ''), ('', '+', '', '', ''),
                                                ('', '', '', '', '1')]),
                              ("abs(1d6)", [('', '', '', 'abs', ''), ('', '', '(', '', ''), ('1d6', '', '', '', ''),
                                            ('', '', ')', '', '')]),
                              ("(10d10k5+1d6)-3", [('', '', '(', '', ''), ('10d10k5', '', '', '', ''),
                                                   ('', '+', '', '', ''), ('1d6', '', '', '', ''),
                                                   ('', '', ')', '', ''), ('', '-', '', '', ''),
                                                   ('', '', '', '', '3')]),
                              ("5", [('', '', '', '', '5')])
                              ]
                             )
    async def test_roll_parse(roll, result):
        assert (await Gambler.parse_roll(roll)) == result
