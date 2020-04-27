"""
This file holds Smorg's database implementation. Currently, it applies sqlalchemy to perform most of its operations.
It contains, firstly, the BaseAddition mix-in that adds a couple utilities to each of the database tables.
Second, it defines three tables as various operations related to them: Guild, Quote, and Reminder.
"""

from __future__ import annotations

import sqlalchemy

from datetime import datetime
from discord import Message
from discord.ext.commands import Bot
from functools import wraps
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, query
from typing import Callable, Union

import secretbord
from Cogs.Helpers.Enumerators.universalist import DiscordConstant


engine = sqlalchemy.create_engine(
    f"{secretbord.database}+{secretbord.dialect}://{secretbord.username}:{secretbord.password}@"
    f"{secretbord.host}:{secretbord.port}/{secretbord.database_name}",
    connect_args=secretbord.options, echo=True
)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


class BaseAddition:
    """
    This class is a mix-in for database tables to provide them with convenient functionality.
    The session_method function is a decorator that makes setting up and tearing down database actions more streamlined.
    The reset_database function performs an auto-reset on the database and is useful for testing purposes and
    for updating the structure of the database as needed.
    """
    @classmethod
    def session_method(cls, decorated_function: Callable) -> Callable:
        """
        This function is a decorator that automatically sets up and closes sessions for database connections.

        :param Callable decorated_function: any function for which a Session is relevant.
        :return Callable: a version of decorated_function which starts by opening a Session and
        ends by closing it.
        """
        @wraps(decorated_function)
        def session_decorator(*args, **kwargs):
            method_session: Session = Session()
            session_value = decorated_function(method_session, *args, **kwargs)
            method_session.close()
            return session_value
        return session_decorator

    @staticmethod
    def reset_database() -> None:
        """
        This method resets the database down to the structure based upon the classes described below.
        """
        Base.metadata.drop_all()
        Base.metadata.create_all()


class Quote(BaseAddition, Base):
    """
    This class represents a quotation stored from a Guild for the SQLAlchemy ORM.
    """
    __tablename__ = 'quotes'

    # Attributes:
    author = Column(String(DiscordConstant.MAX_ROLE_LENGTH), nullable=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.guild_id'), nullable=False)
    quote_id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False)
    last_updated_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False,
                             onupdate=sqlalchemy.sql.func.now())

    # Relationships:
    guild = relationship("Guild", back_populates="quotes")

    # Methods:
    def __repr__(self):
        return f'<Quote(author: {self.author}, guild_id: {self.guild_id}, quote_id: {self.quote_id}, ' \
               f'text: {self.text}, created_at: {self.created_at}, last_updated_at: {self.last_updated_at})>'

    # Queries:
    @staticmethod
    @BaseAddition.session_method
    def count_quotes(method_session: Session, g_id: int) -> int:
        """
        This method counts the number of quotes that a Guild has stored in the database.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :return int: the number of quotes which belong to a given Guild.
        """
        count = method_session.query(Quote).filter_by(guild_id=g_id).count()
        return count

    @staticmethod
    @BaseAddition.session_method
    def create_quote_with(method_session: Session, g_id: int, quote: str, auth: str) -> None:
        """
        This method creates and stores a Quote in the database.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :param str quote: the text of the quotation.
        :param str auth: the author of the quotation.
        """
        new_quote = Quote(author=auth, guild_id=g_id, text=quote)
        method_session.add(new_quote)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_quotes_by(method_session: Session, g_id: int, auth: Union[str, None] = None) -> list:
        """
        This method retrieves quotes based on the criteria of a Guild's ID and, optionally, a specific author.

        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID.
        :param auth: the author of the quotation.
        :return list: collection of authors and quotations from Quote objects that fulfill the given criteria.
        """
        if auth:
            quote_list: list = method_session.query(Quote.author, Quote.text).filter_by(guild_id=g_id, author=auth) \
                .all()
        else:
            quote_list: list = method_session.query(Quote.author, Quote.text).filter_by(guild_id=g_id).all()
        return quote_list

    @staticmethod
    @BaseAddition.session_method
    def get_random_quote_by(method_session: Session, g_id: int, q_number: int) -> Quote:
        """
        This method retrieves a random quote from a given server from the database.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :param int q_number: a random number less than the maximum number of quotes that a server has.
        :return Quote: a Quote object randomly selected from a given Guild.
        """
        quote: Quote = method_session.query(Quote).filter_by(guild_id=g_id).all()[q_number]
        return quote


class Reminder(Base, BaseAddition):
    """
    This class represents a reminder stored from a Guild for the SQLAlchemy ORM.
    Once Smorg pings a role with a Reminder, that Reminder is deleted.
    """
    __tablename__ = 'reminders'

    guild_id = Column(BigInteger, ForeignKey('guilds.guild_id'), primary_key=True, nullable=False)
    mentionable = Column(String(100), primary_key=True, nullable=False)
    reminder_datetime = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    reminder_text = Column(String(DiscordConstant.MAX_EMBED_FIELD_VALUE), nullable=True)
    created_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False)
    last_updated_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False,
                             onupdate=sqlalchemy.sql.func.now())

    # Relationships:
    guild = relationship("Guild", back_populates="reminders")

    # Methods:
    def __repr__(self) -> str:
        return f'<Reminder(guild_id: {self.guild_id}, mentionable: {self.mentionable}, ' \
               f'reminder_datetime: {self.reminder_datetime}, reminder_text: {self.reminder_text}, ' \
               f'created_at: {self.created_at}, last_updated_at: {self.last_updated_at})>'

    @staticmethod
    @BaseAddition.session_method
    def create_reminder_with(method_session: Session, g_id: int, mentionable: str, r_text: Union[str, None],
                             r_datetime: datetime) -> None:
        """
        This method creates a Reminder with a given mentionable, datetime, and optional message.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :param str mentionable: text representing a Role or Member's mention.
        :param Union[str, None] r_text: text referring to what the Role or Member should be reminded about.
        :param datetime r_datetime: the date and time at which the Reminder will be sent.
        """
        new_guild = Reminder(guild_id=g_id, mentionable=mentionable, reminder_text=r_text, reminder_datetime=r_datetime)
        method_session.add(new_guild)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def update_reminder_with(method_session: Session, g_id: int, mention: str, old_r_datetime: datetime,
                             new_r_datetime: Union[datetime, None], new_r_text: Union[str, None]) -> None:
        """
        This method updates a Reminder with a new datetime and/or new text.

        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID.
        :param mention: text representing a Role or Member's mention.
        :param datetime old_r_datetime: the old date and time at which the Reminder will be sent.
        :param Union[datetime, None] new_r_datetime: the new date and time at which the Reminder will be sent.
        :param Union[str, None] new_r_text: the new text referring to what the Role or Member should be reminded about.
        """
        attributes_to_update: dict = {}
        reminder_to_update: query = method_session.query(Reminder).filter_by(
            guild_id=g_id, mentionable=mention, reminder_datetime=old_r_datetime
        )
        if new_r_datetime:
            attributes_to_update["reminder_datetime"] = new_r_datetime
        if new_r_text:
            attributes_to_update["reminder_text"] = new_r_text
        reminder_to_update.update(attributes_to_update)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_reminders_by(method_session: Session, g_id: int, mention: str) -> list:
        """
        This method retrieves reminder datetimes and messages that are in some Guild and apply to a given mentionable.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :param str mention: text representing a Role or Member's mention.
        :return list: a collection of Reminder datetimes and messages that meet the above criteria.
        """
        reminder_list: list = method_session.query(Reminder.reminder_datetime, Reminder.reminder_text).filter_by(
            guild_id=g_id, mentionable=mention
        ).all()
        return reminder_list

    @staticmethod
    @BaseAddition.session_method
    def pop_reminders_at(method_session: Session, relevant_datetime: datetime) -> list:
        """
        This method retrieves all Reminders that have passed some time.
        It sends these back to the calling function and deletes them from the database.

        :param method_session: a Session database connection.
        :param datetime relevant_datetime: a time to which Reminder's datetimes will be compared.
        :return list: a collection of Reminder objects that occurred before relevant_datetime.
        """
        reminder_list: list = method_session.query(Reminder) \
            .filter(Reminder.reminder_datetime <= relevant_datetime).all()
        for reminder in reminder_list:
            Reminder.delete_reminder_with(
                g_id=reminder.guild_id, mention=reminder.mentionable, scheduled_time=reminder.reminder_datetime
            )
        return reminder_list

    @staticmethod
    @BaseAddition.session_method
    def has_reminder_with(method_session: Session, g_id: int, mention: str, scheduled_time: datetime) -> bool:
        """
        This method determines whether there's a Reminder with a given mention and datetime.

        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID.
        :param mention: text representing a Role or Member's mention.
        :param scheduled_time: a date and time at which a Reminder might be sent.
        :return bool: True if a Reminder with the given criteria exists; False, otherwise.
        """
        scheduled_reminder: Reminder = method_session.query(Reminder).filter_by(
            guild_id=g_id, mentionable=mention, reminder_datetime=scheduled_time
        ).first()
        return True if scheduled_reminder else False

    @staticmethod
    @BaseAddition.session_method
    def delete_reminder_with(method_session: Session, g_id: int, mention: str, scheduled_time: datetime) -> None:
        """
        This method deletes a Reminder if one exists that meets the given criteria: a Guild, a mention, and a datetime.

        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID.
        :param mention: text representing a Role or Member's mention.
        :param scheduled_time: a date and time at which a Reminder might be sent.
        """
        method_session.query(Reminder).filter_by(
            guild_id=g_id, mentionable=mention, reminder_datetime=scheduled_time
        ).delete()
        method_session.commit()


class Guild(Base, BaseAddition):
    """
    This class represents a Discord server, called a Guild. It is the main table which other tables rely on.
    """
    __tablename__ = 'guilds'

    # Attributes:
    guild_id = Column(BigInteger, primary_key=True, nullable=False)
    gamble_channel_id = Column(BigInteger, unique=True, nullable=True)
    guild_prefix = Column(String, default='.', nullable=False)
    quotation_channel_id = Column(BigInteger, unique=True, nullable=True)
    reminder_channel_id = Column(BigInteger, unique=True, nullable=True)
    created_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False)
    last_updated_at = Column(DateTime, default=sqlalchemy.sql.func.now(),
                             nullable=False, onupdate=sqlalchemy.sql.func.now())

    # Relationships:
    quotes = relationship("Quote", order_by=Quote.quote_id, back_populates="guild", cascade="delete")
    reminders = relationship(
        "Reminder", order_by=Reminder.reminder_datetime, back_populates="guild", cascade="delete"
    )

    # Methods:
    def __repr__(self):
        return f'<Guild(guild_id: {self.guild_id}, gamble_channel_id: {self.gamble_channel_id}, ' \
               f'guild_prefix: {self.guild_prefix}, quotation_channel_id: {self.quotation_channel_id}, ' \
               f'reminder_channel_id: {self.reminder_channel_id}, created_at: {self.created_at}, ' \
               f'last_updated_at: {self.last_updated_at})>'

    # Queries:
    @staticmethod
    @BaseAddition.session_method
    def get_quotation_channel_by(method_session: Session, g_id: int) -> Union[int, None]:
        """
        This method retrieves the quotation channel for a given Guild.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :return Union[int, None]: the Guild's quotation channel ID, if it exists.
        """
        quotation_channel = method_session.query(Guild.quotation_channel_id).filter_by(guild_id=g_id).first()
        return quotation_channel[0]

    @staticmethod
    @BaseAddition.session_method
    def exists_with(method_session: Session, g_id: int) -> bool:
        """
        This method determines whether a Guild is known to Smorg.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :return bool: True, if a Guild exists; False, otherwise.
        """
        guild: Guild = method_session.query(Guild).filter_by(guild_id=g_id).first()
        return True if guild else False

    @staticmethod
    @BaseAddition.session_method
    def create_guild_with(method_session: Session, g_id: int, c_id: Union[int, None]) -> None:
        """
        This method creates a Guild and stores it in the database.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :param int c_id: a Discord Channel ID.
        """
        new_guild = Guild(guild_id=g_id, quotation_channel_id=c_id, reminder_channel_id=c_id)
        method_session.add(new_guild)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def delete_guild_with(method_session: Session, g_id: int) -> None:
        """
        This method deletes a Guild with the given Guild ID.

        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID.
        """
        method_session.query(Guild).filter_by(guild_id=g_id).delete()
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def update_quotation_channel(method_session: Session, g_id: int, c_id: int) -> None:
        """
        This method retrieves a Guild and updates its quotation channel.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :param int c_id: a Discord Channel ID.
        """
        method_session.query(Guild).filter_by(guild_id=g_id).update({"quotation_channel_id": c_id})
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_reminder_channel_by(method_session: Session, g_id: int) -> int:
        """
        This method retrieves the reminder channel for a given Guild.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :return int: a channel ID.
        """
        reminder_channel = method_session.query(Guild.reminder_channel_id).filter_by(guild_id=g_id).first()
        return reminder_channel[0]

    @staticmethod
    @BaseAddition.session_method
    def update_reminder_channel(method_session: Session, g_id: int, c_id: int) -> None:
        """
        This method retrieves a Guild and updates its quotation channel.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :param int c_id: a Discord Channel ID.
        """
        method_session.query(Guild).filter_by(guild_id=g_id).update({"reminder_channel_id": c_id})
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_gamble_channel_by(method_session: Session, g_id: int) -> int:
        """
        This method retrieves the gamble channel for a given Guild.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :return int: a channel ID.
        """
        reminder_channel = method_session.query(Guild.gamble_channel_id).filter_by(guild_id=g_id).first()
        return reminder_channel[0]

    @staticmethod
    @BaseAddition.session_method
    def update_gamble_channel(method_session: Session, g_id: int, c_id: int) -> None:
        """
        This method retrieves a Guild and updates its gamble channel.

        :param method_session: a Session database connection.
        :param int g_id: a Discord Guild ID.
        :param int c_id: a Discord Channel ID.
        """
        method_session.query(Guild).filter_by(guild_id=g_id).update({"gamble_channel_id": c_id})
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_prefix(method_session: Session, bot: Bot, message: Message) -> str:
        """
        This method retrieves the command prefix that must begin each of Smorg's commands.

        :param method_session: a Session database connection.
        :param Bot bot: the Bot instance for which the given prefix is relevant.
        :param Message message: the Discord message for which a prefix must be identified.
        :return str: the character(s) of a specified Guild's command prefix.
        """
        g_id: int = message.channel.guild.id
        guild_prefix: list = method_session.query(Guild.guild_prefix).filter_by(guild_id=g_id).first()
        return guild_prefix[0] if guild_prefix else '.'

    @staticmethod
    @BaseAddition.session_method
    def update_prefix(method_session: Session, g_id: int, new_prefix: str) -> None:
        """
        This method updates the command prefix that must begin each of Smorg's commands.

        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID.
        :param new_prefix: a series of characters that specifies a new prefix for the Guild's commands to Smorg.
        """
        method_session.query(Guild).filter_by(guild_id=g_id).update({"guild_prefix": new_prefix})
        method_session.commit()
