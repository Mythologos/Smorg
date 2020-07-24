# Smorg
**Last Updated:** 07/22/2020 (MM/DD/YYYY)

## Introduction

Hello! Welcome to Smorg, a [Discord](https://discordapp.com/) bot with a variety of useful functions built with [discord.py](https://discordpy.readthedocs.io/en/latest/index.html). It is being worked on as a personal project for the author to improve his programming prowess. It has been publicized as a resource and reference for other programmers in building their own Discord bots.

While this bot is displayed in a public repository, it is currently intended for a select group of servers while it continues to grow and improve. I have not provided instructions on setting up Smorg as a result, and I ask that you do not currently use Smorg as more than as referential material.

## Functionality

Smorg can currently perform the following tasks:
1. The **help** command displays a help menu as a Discord embed. As more commands are added, the embed can generate more fields automatically and create further embeds as necessary.
2. The **govern** command allows members of a Discord guild to allocate certain operations that Smorg can perform to specific channels. The subcommands that relate to this operation include: *gamble*, *reminder*, and *quotation*.
3. The **display** command uses embeds to visualize various information about Smorg. The subcommands *reminders* and *quotes* present information about Smorg's current state relative to the guild. Meanwhile, the subcommands *dice*, *functions*, *operators*, and *zones* present general information about Smorg's processes.
4. The **observe** command permits the user to change the prefix to which Smorg responds in a specific guild.
5. The **purge** command lets the user delete the last n messages, where n is a specified number, or messages between two specified dates and times. This message count and specified times can also be combined in various ways.
6. The **roll** command rolls dice with adaptive and flexible roll syntax and full capability to include extensive operations and modifiers inside the roll. Embeds are used in the process of displaying detailed results concerning the roll.
7. The **translate** command converts characters in a specified starting character set to a specified target character set. The only supported character sets currently are *alphabet* (e.g. Latin alphabet) and *morse*. Currently, *morse* can only be written with special characters (which Smorg also produces).
8. The **quote** command embeds a quote for display. It requires a quote and an optional author argument.
9. The **immortalize** command does as **quote** does, but it also stores the quote in Smorg's database.
10. The **yoink** command retrieves a random quote from Smorg's database for display.
11. The **remind** command allows the user to choose a role and schedule a time at which Smorg will ping that role. It can also include an optional message. 
12. The **revise** command lets the user specify a reminder and then supply either a new time, a new message, or both. Smorg then changes the reminder to meet these specifications.
13. The **forget** command permits the user to delete a reminder by specifying it.

## Future Goals:

As this is a personal project and I end up having progressively more ideas as I learn more about what's possible and optimal, there's still a lot left to do! The below list is for my own reference, as Smorg is currently not a collaborative project. However, if you have suggestions about Smorg, feel free to let me know!
1. Create an easier way to write morse code as periods and dashes for `encoder.py`.
2. Create a way to convert morse code into sound files that can be uploaded and played.
3. Investigate asynchronous database options (e.g. [asyncpg](https://github.com/MagicStack/asyncpg), [asyncpgsa](https://github.com/CanopyTax/asyncpgsa), [aiopg](https://github.com/aio-libs/aiopg/), [GINO](https://github.com/python-gino/gino), others?) and implement asynchronous solutions to mesh with the asynchronous foundation of a discord bot.
4. Implement a deck of cards into the bot for use in the gamble Cog. Should it merely draw cards? Should it play games? How stateful should it be per server?
5. Revive the idea behind `disambiguator.py` as some kind of polling feature.
6. Let `yard_shunter.py` and `tabulator.py` work with functions or operators that have varied numbers of operands (e.g. `!` being an operator that takes one operand as opposed to two).
7. Implement a (very late) test suite to assure that features don't break as I tinker with, optimize, and abstract older methods.
8. Synthesize database methods to make database processing sleeker.
9. Add more character sets for encoder to translate between.
10. Condense the universal error-handling in `hearer.py` by using a dictionary to relate errors and error descriptions.
11. Add multilingual support for Smorg commands (storing aliases in `polyglot.py`?).
12. Find a better way to access dictionary constants, especially for `encoder.py`'s character set translations.
13. Change the to_target_language methods in the `encoder` Cog to be flexible to the from_language argument.
14. Differentiate some nomenclature (e.g. `discord.Guild` vs. Guild database table) to help improve import optimization.
15. Add more extensive type hints with typing's data structures (e.g. `List`, `Tuple`).
16. If reasonable, shift some of the `display` Command's functionality to the `support` Command, as some (but not all) of `display`'s uses are more like non-command helper Embeds.
17. Have the anonymous value of an `author` for quotes be alterable per Guild.
18. Allow for the inclusion of raw decimals in `gambler.py` and `yard_shunter.py`'s algorithms.
19. Allow for `consolidate_tokens()` to do more pre-processing in `yard_shunter.py` and shorten the function (if any of this is deemed beneficial).
20. Change `OperatorAssociativity` to hold integers, if possible, instead of strings.
21. Integrate color more flexibly in commands. Make a tool or command that allows a user to specify a color; Smorg returns this color against various Discord UI backgrounds (e.g. light vs. dark).