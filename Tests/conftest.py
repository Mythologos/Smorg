# TODO: description

import pytest
import discord.ext.test as dpytest
from Bot.smorgasbord import Smorg


@pytest.fixture(scope='session')
def smorg_bot():
    # Setup:
    test_smorg_bot: Smorg = Smorg()
    dpytest.configure(test_smorg_bot)
    universal_test_guild = dpytest.backend.make_guild("Test Guild")
    dpytest.backend.make_text_channel("general", universal_test_guild)
    universal_test_user = dpytest.backend.make_user("WolfMirage", "9601")
    dpytest.backend.make_member(universal_test_user, universal_test_guild, "Woofy")

    # Tests:
    yield

    # Teardown:
    ...


# Fixtures for testing database items should be stored in a wider level (session, perhaps);
# other fixtures could be stored in Cog-specific files.