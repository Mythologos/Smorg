"""
This is the initialization file for Smorg. It initializes an AutoShardedBot instance with command prefixes
determined by the database method get_prefix(). It removes the default help command for Discord bots.
Then, it adds each Cog that the bot currently supports and starts the bot with its corresponding bot key.
"""

from discord.ext.commands import AutoShardedBot

from Cogs.arranger import Arranger
from Cogs.cataloguer import Cataloguer
from Cogs.encoder import Encoder
from Cogs.gambler import Gambler
from Cogs.hearer import Hearer
from Cogs.helper import Helper
from Cogs.quoter import Quoter
from Cogs.recaller import Recaller
from secretbord import bot_key
from smorgasDB import Guild

smorg = AutoShardedBot(command_prefix=Guild.get_prefix)
smorg.remove_command('help')
smorg.add_cog(Arranger(smorg))
smorg.add_cog(Cataloguer(smorg))
smorg.add_cog(Hearer(smorg))
smorg.add_cog(Helper(smorg))
smorg.add_cog(Quoter(smorg))
smorg.add_cog(Recaller(smorg))
smorg.add_cog(Gambler(smorg))
smorg.add_cog(Encoder(smorg))

smorg.run(bot_key)
