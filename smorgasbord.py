# TODO: MODULAR DOCUMENTATION
# TODO: handle deleted channels case

import discord
from discord.ext import commands
import secretbord

from Cogs.arranger import Arranger
from Cogs.hearer import Hearer
from Cogs.helper import Helper
from Cogs.quoter import Quoter
from Cogs.recaller import Recaller

smorg = commands.AutoShardedBot(command_prefix='.')
smorg.remove_command('help')
smorg.add_cog(Arranger(smorg))
smorg.add_cog(Hearer(smorg))
smorg.add_cog(Helper(smorg))
smorg.add_cog(Quoter(smorg))
smorg.add_cog(Recaller(smorg))

smorg.run(secretbord.bot_key)
