# TODO: will implement general tests related to the bot and the existence of its components

import pytest


class TestRecognition:
    @staticmethod
    async def test_has_guild(smorg_bot):
        state = smorg_bot.get_state()
        print("Here is the state. ", state, "There was the state.")
        assert 1 == 2

    @staticmethod
    async def test_has_user(smorg_bot):
        assert 1 == 2

    @staticmethod
    async def test_has_channel(smorg_bot):
        assert 1 == 2
