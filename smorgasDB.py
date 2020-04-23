# TODO: MODULAR DOCUMENTATION
# TODO: handle deleted channels case for various tables here
# TODO: use query for type hints (as items retrieved are query.Query items)

from __future__ import annotations

import datetime
import discord
import sqlalchemy

from discord.ext import commands
from functools import wraps
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, query
from sqlalchemy import Column, ForeignKey
from sqlalchemy import BigInteger, DateTime, SmallInteger, String
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


# TODO: describe this as a mixin.
class BaseAddition:
    @classmethod
    def session_method(cls, decorated_function: Callable) -> Callable:
        """
        Decorator; automatically sets up and closes sessions for database connections.
        :param decorated_function: a function that requires a session.
        :return: a function with the built-in capability of opening and closing a session.
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
        TODO -- should this be placed somewhere else?
        This method resets the database down to the structure based upon the classes described above.
        :return: None.
        """
        Base.metadata.drop_all()
        Base.metadata.create_all()


class Quote(BaseAddition, Base):
    """
    This class represents a quote stored from a server.
    """
    __tablename__ = 'quotes'

    # Attributes:
    author = Column(String(DiscordConstant.MAX_ROLE_LENGTH), nullable=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.guild_id'), nullable=False)
    quote_id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False)
    last_updated_at = Column(DateTime, default=sqlalchemy.sql.func.now(),
                             nullable=False, onupdate=sqlalchemy.sql.func.now())

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
        :param g_id: a Discord Guild ID (Integer).
        :return: the number of quotes which belong to a given Guild (an Integer).
        """
        count = method_session.query(Quote).filter_by(guild_id=g_id).count()
        return count

    @staticmethod
    @BaseAddition.session_method
    def create_quote_with(method_session: Session, g_id: int, quote: str, auth: str) -> None:
        """
        This method creates and stores a Quote in the database.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param quote: the text of the quotation (String).
        :param auth: the author of the quotation (String).
        :return: None.
        """
        new_quote = Quote(author=auth, guild_id=g_id, text=quote)
        method_session.add(new_quote)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_quotes_by(method_session: Session, g_id: int, auth: Union[str, None] = None) -> list:
        if auth:
            quote_list = method_session.query(Quote.author, Quote.text).filter_by(guild_id=g_id, author=auth)
        else:
            quote_list = method_session.query(Quote.author, Quote.text).filter_by(guild_id=g_id)
        return quote_list

    @staticmethod
    @BaseAddition.session_method
    def get_random_quote_by(method_session: Session, g_id: int, q_number: int) -> str:
        """
        This method retrieves a random quote from a given server from the database.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param q_number: a random number less than the maximum number of quotes that a server has.
        :return: a Quote's author and text, in that order, in a Tuple.
        """
        quote = method_session.query(Quote.author, Quote.text).filter_by(guild_id=g_id)[q_number]
        return quote


class Reminder(Base, BaseAddition):
    __tablename__ = 'reminders'

    guild_id = Column(BigInteger, ForeignKey('guilds.guild_id'), primary_key=True, nullable=False)
    mentionable = Column(String(100), primary_key=True, nullable=False)
    reminder_datetime = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    reminder_text = Column(String(DiscordConstant.MAX_EMBED_FIELD_VALUE), nullable=True)
    created_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False)
    last_updated_at = Column(DateTime, default=sqlalchemy.sql.func.now(),
                             nullable=False, onupdate=sqlalchemy.sql.func.now())

    # Relationships:
    guild = relationship("Guild", back_populates="reminders")

    # Methods:
    def __repr__(self) -> str:
        return f'<Reminder(guild_id: {self.guild_id}, mentionable: {self.mentionable}, ' \
               f'reminder_datetime: {self.reminder_datetime}, reminder_text: {self.reminder_text}, ' \
               f'created_at: {self.created_at}, last_updated_at: {self.last_updated_at})>'

    @staticmethod
    @BaseAddition.session_method
    def create_reminder_with(method_session: Session, g_id: int, mentionable: str, r_text: str,
                             r_datetime: datetime.datetime) -> None:
        new_guild = Reminder(guild_id=g_id, mentionable=mentionable, reminder_text=r_text, reminder_datetime=r_datetime)
        method_session.add(new_guild)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def update_reminder_with(method_session: Session, g_id: int, mention: str, old_r_datetime: datetime.datetime,
                             new_r_datetime: datetime.datetime, new_r_text: str) -> None:
        attributes_to_update: dict = {}
        reminder_to_update: query = method_session.query(Reminder) \
            .filter_by(guild_id=g_id, mentionable=mention, reminder_datetime=old_r_datetime)
        if new_r_datetime:
            attributes_to_update["reminder_datetime"] = new_r_datetime
        if new_r_text:
            attributes_to_update["reminder_text"] = new_r_text
        reminder_to_update.update(attributes_to_update)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_reminders_by(method_session: Session, g_id: int, mention: str) -> list:
        reminder_list: list = method_session.query(Reminder.reminder_datetime, Reminder.reminder_text) \
            .filter_by(guild_id=g_id, mentionable=mention)
        return reminder_list

    @staticmethod
    @BaseAddition.session_method
    def pop_reminders_at(method_session: Session, current_datetime: datetime.datetime):
        reminder_list: list = method_session.query(Reminder) \
            .filter(Reminder.reminder_datetime <= current_datetime).all()
        for reminder in reminder_list:
            Reminder.delete_reminder_with(
                g_id=reminder.guild_id, mention=reminder.mentionable, scheduled_time=reminder.reminder_datetime
            )
        return reminder_list

    @staticmethod
    @BaseAddition.session_method
    def has_reminder_with(method_session: Session, g_id: int, mention: str, scheduled_time: datetime.datetime) -> bool:
        scheduled_reminder: Reminder = method_session.query(Reminder) \
            .filter_by(guild_id=g_id, mentionable=mention, reminder_datetime=scheduled_time).first()
        return True if scheduled_reminder else False

    @staticmethod
    @BaseAddition.session_method
    def delete_reminder_with(method_session: Session, g_id: int, mention: str,
                             scheduled_time: datetime.datetime) -> None:
        method_session.query(Reminder).filter_by(guild_id=g_id, mentionable=mention, reminder_datetime=scheduled_time) \
            .delete()
        method_session.commit()


class Guild(Base, BaseAddition):
    """
    This class represents a Discord server, called a Guild.
    """
    __tablename__ = 'guilds'

    # Attributes:
    guild_id = Column(BigInteger, primary_key=True, nullable=False)
    gamble_channel_id = Column(BigInteger, unique=True, nullable=True)
    guild_prefix = Column(String, default='.', nullable=False)
    quotation_channel_id = Column(BigInteger, unique=True, nullable=False)
    reminder_channel_id = Column(BigInteger, unique=True, nullable=False)
    created_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False)
    last_updated_at = Column(DateTime, default=sqlalchemy.sql.func.now(),
                             nullable=False, onupdate=sqlalchemy.sql.func.now())

    # Relationships:
    quotes = relationship("Quote", order_by=Quote.quote_id, back_populates="guild")
    reminders = relationship("Reminder", order_by=[Reminder.reminder_datetime],
                             back_populates="guild")

    # Methods:
    def __repr__(self):
        return f'<Guild(guild_id: {self.guild_id}, gamble_channel_id: {self.gamble_channel_id}, ' \
               f'guild_prefix: {self.guild_prefix}, quotation_channel_id: {self.quotation_channel_id}, ' \
               f'reminder_channel_id: {self.reminder_channel_id}, created_at: {self.created_at}, ' \
               f'last_updated_at: {self.last_updated_at})>'

    # Queries:
    @staticmethod
    @BaseAddition.session_method
    def get_quotation_channel_by(method_session: Session, g_id: int) -> int:
        """
        This method retrieves the quotation channel for a given Guild.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :return: a channel ID (Integer).
        """
        quotation_channel = method_session.query(Guild.quotation_channel_id).filter_by(guild_id=g_id).first()
        return quotation_channel[0]

    @staticmethod
    @BaseAddition.session_method
    def exists_with(method_session: Session, g_id: int) -> bool:
        """
        This method determines whether a Guild has channels assigned to it.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :return: a Boolean of whether a Guild has a channel quotation to it according to the database.
        """
        guild_id = method_session.query(Guild.guild_id).filter_by(guild_id=g_id).first()
        is_guild = guild_id is not None
        return is_guild

    @staticmethod
    @BaseAddition.session_method
    def create_guild_with(method_session: Session, g_id: int, c_id: int):
        """
        This method creates a Guild and stores it in the database.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param c_id: a Discord Channel ID (Integer).
        :return: None.
        """
        new_guild = Guild(guild_id=g_id, quotation_channel_id=c_id, reminder_channel_id=c_id)
        method_session.add(new_guild)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def update_quotation_channel(method_session: Session, g_id: int, c_id: int):
        """
        This method retrieves a Guild and updates its quotation channel.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param c_id: a Discord Channel ID (Integer).
        :return: None.
        """
        method_session.query(Guild) \
                      .filter_by(guild_id=g_id) \
                      .update({"quotation_channel_id": c_id})
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_reminder_channel_by(method_session: Session, g_id: int) -> int:
        """
        This method retrieves the reminder channel for a given Guild.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :return: a channel ID (Integer).
        """
        reminder_channel = method_session.query(Guild.reminder_channel_id).filter_by(guild_id=g_id).first()
        return reminder_channel[0]

    @staticmethod
    @BaseAddition.session_method
    def update_reminder_channel(method_session: Session, g_id: int, c_id: int) -> None:
        """
        This method retrieves a Guild and updates its quotation channel.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param c_id: a Discord Channel ID (Integer).
        :return: None.
        """
        method_session.query(Guild) \
                      .filter_by(guild_id=g_id) \
                      .update({"reminder_channel_id": c_id})
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_gamble_channel_by(method_session: Session, g_id: int) -> int:
        """
        This method retrieves the gamble channel for a given Guild.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :return: a channel ID (Integer).
        """
        reminder_channel = method_session.query(Guild.gamble_channel_id).filter_by(guild_id=g_id).first()
        return reminder_channel[0]

    @staticmethod
    @BaseAddition.session_method
    def update_gamble_channel(method_session: Session, g_id: int, c_id: int) -> None:
        """
        This method retrieves a Guild and updates its gamble channel.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param c_id: a Discord Channel ID (Integer).
        :return: None.
        """
        method_session.query(Guild) \
                      .filter_by(guild_id=g_id) \
                      .update({"gamble_channel_id": c_id})
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def get_prefix(method_session: Session, bot: commands.Bot, message: discord.Message):
        g_id: int = message.channel.guild.id
        guild_prefix = method_session.query(Guild.guild_prefix).filter_by(guild_id=g_id).first()
        return guild_prefix[0]

    @staticmethod
    @BaseAddition.session_method
    def update_prefix(method_session: Session, g_id: int, new_prefix: str):
        method_session.query(Guild) \
                      .filter_by(guild_id=g_id) \
                      .update({"guild_prefix": new_prefix})
        method_session.commit()
