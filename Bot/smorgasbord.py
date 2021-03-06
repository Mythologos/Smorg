"""
This file defines the Smorg class, inserting all Cogs into one AutoShardedBot instance.
It removes the default help command and inserts the bot's Discord key.
By having it as a class, it can be more formally created and run at separate times and in multiple instances.
"""

from discord.ext.commands import AutoShardedBot

from .Cogs.arranger import Arranger
from .Cogs.cataloguer import Cataloguer
from .Cogs.encoder import Encoder
from .Cogs.gambler import Gambler
from .Cogs.hearer import Hearer
from .Cogs.helper import Helper
from .Cogs.logger import Logger
from .Cogs.quoter import Quoter
from .Cogs.recaller import Recaller
from .secretbord import bot_key
from .smorgasDB import Guild


class Smorg:
    def __init__(self):
        self.bot = AutoShardedBot(command_prefix=Guild.get_prefix)
        self.bot.remove_command('help')

        for cog in [Arranger, Cataloguer, Encoder, Gambler, Hearer, Helper, Logger, Quoter, Recaller]:
            self.bot.add_cog(cog(self.bot))

    def run(self):
        self.bot.run(bot_key)
