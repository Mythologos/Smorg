# TODO: will implement general tests related to the bot and the existence of its components

import discord.ext.test as dpytest
import pytest

from Bot.smorgasbord import Smorg

# Not sure if using a class like this is a good idea.
# How should I proceed? What's the best way to set all of these tests up? Does my setup function work?


class TestRunner:
    def __init__(self):
        smorg_bot = Smorg()
        dpytest.configure(smorg_bot)
        await self.setup_test_guild()

    @staticmethod
    async def setup_test_guild():
        test_guild = dpytest.backend.make_guild("Test Guild")
        dpytest.backend.make_text_channel("general", test_guild)
        test_user = dpytest.backend.make_user("WolfMirage", "9601")
        dpytest.backend.make_member(test_user, test_guild, "Woofy")

    @pytest.mark.asyncio
    async def test_bot(self):
        ...
