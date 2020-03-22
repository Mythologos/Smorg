# TODO: MODULAR DOCUMENTATION
# Add: flush/purge command for messages, a command to change the bot's prefix.

from discord.ext import commands

import secretbord
from smorgasDB import Guild
from Cogs.arranger import Arranger
from Cogs.hearer import Hearer
from Cogs.helper import Helper
from Cogs.quoter import Quoter
from Cogs.recaller import Recaller
from Cogs.gambler import Gambler
from Cogs.encoder import Encoder

smorg = commands.AutoShardedBot(command_prefix=Guild.get_prefix)
smorg.remove_command('help')
smorg.add_cog(Arranger(smorg))
smorg.add_cog(Hearer(smorg))
smorg.add_cog(Helper(smorg))
smorg.add_cog(Quoter(smorg))
smorg.add_cog(Recaller(smorg))
smorg.add_cog(Gambler(smorg))
smorg.add_cog(Encoder(smorg))

smorg.run(secretbord.bot_key)
