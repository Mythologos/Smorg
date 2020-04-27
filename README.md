# Smorg
**Last Updated:** 04/24/2020 (MM/DD/YYYY)

Hello! Welcome to Smorg, a Discord bot with a variety of useful functions.

This description is a work-in-progress! Thank you for visiting this repository.

**Current Functionality:**
(TODO)

**Future To-Do List (in no particular order):**
1. Create an easier way to write morse code as periods and dashes for `encoder.py`.
2. Create a way to convert morse code into sound files that can be uploaded and played.
3. Investigate asynchronous database options (e.g. [asyncpg](https://github.com/MagicStack/asyncpg), [asyncpgsa](https://github.com/CanopyTax/asyncpgsa), [aiopg](https://github.com/aio-libs/aiopg/), [GINO](https://github.com/python-gino/gino), others?) and implement asynchronous solutions to mesh with the asynchronous foundation of a discord bot.
4. Implement a deck of cards into the bot for use in the gamble Cog. Should it merely draw cards? Should it play games? How stateful should it be per server?
5. Revive the idea behind `disambiguator.py` as some kind of polling feature.
6. Let `yard_shunter.py` and `tabulator.py` work with functions or operators that have varied numbers of operands (e.g. `!` being an operator that takes one operand as opposed to two).
7. Implement a test suite to assure that features don't break as I tinker with, optimize, and abstract older methods.
8. Synthesize database methods to make database processing sleeker.
9. Add more character sets for encoder to translate between.
10. Condense the universal error-handling in hearer.py by using a dictionary to relate errors and error descriptions.
11. Add multilingual support for Smorg commands (storing aliases in polyglot.py?).
12. Find a better way to access dictionary constants, especially for encoder.py's character set translations.
13. Change the to_target_language methods in the encoder Cog to be flexible to the from_language argument.
14. Differentiate some nomenclature (e.g. discord.Guild vs. Guild database table) to help improve import optimization.