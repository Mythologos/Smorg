# TODO: description

import discord.ext.test as dpytest
import pytest

from ..Bot.smorgasbord import Smorg
from ..Bot.smorgasDB import BaseAddition


@pytest.fixture(scope='session')
async def smorg_bot():
    # Setup:
    test_smorg_bot: Smorg = Smorg()
    dpytest.configure(test_smorg_bot.bot)
    universal_test_guild = dpytest.backend.make_guild("Test Guild")
    dpytest.backend.make_text_channel("general", universal_test_guild)
    dpytest.backend.make_text_channel("other_general", universal_test_guild)
    universal_test_user = dpytest.backend.make_user("WolfMirage", "9601")
    dpytest.backend.make_member(universal_test_user, universal_test_guild, "Woofy")

    # Tests:
    yield

    # Teardown:
    BaseAddition.reset_database()
