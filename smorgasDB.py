# TODO: MODULAR DOCUMENTATION
# TODO: handle deleted channels case for various tables here

from __future__ import annotations

import sqlalchemy
import discord
from typing import Callable
from discord.ext import commands
from functools import wraps
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, ForeignKey
from sqlalchemy import BigInteger, Date, DateTime, SmallInteger, String, Time

import secretbord


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
    author = Column(String(100), nullable=True)
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
        return f'<Guild(author: {self.author}, guild_id: {self.guild_id}, quote_id: {self.quote_id}, ' \
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
    tag = Column(String(100), primary_key=True, nullable=False)
    tag_text = Column(String)
    reminder_date = Column(Date, nullable=False)
    reminder_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False)
    last_updated_at = Column(DateTime, default=sqlalchemy.sql.func.now(),
                             nullable=False, onupdate=sqlalchemy.sql.func.now())

    # Relationships:
    guild = relationship("Guild", back_populates="reminders")

    # Methods:
    def __repr__(self) -> str:
        return f'<Guild(guild_id: {self.guild_id}, tag: {self.tag}, tag_text: {self.tag_text}, ' \
               f'reminder_date: {self.reminder_date}, reminder_time: {self.reminder_time}, ' \
               f'created_at: {self.created_at}, last_updated_at: {self.last_updated_at})>'

    @staticmethod
    @BaseAddition.session_method
    def create_reminder_with(method_session: Session, g_id: int, tag: str, tag_text: str, date, time) -> None:
        new_guild = Reminder(guild_id=g_id, tag=tag, tag_text=tag_text, reminder_date=date, reminder_time=time)
        method_session.add(new_guild)
        method_session.commit()

    # @staticmethod
    # @BaseAddition.session_method
    # def get_time_zone(method_session):
        # time_zone = method_session.execute("SELECT current_setting('TIMEZONE');").fetchall()[0][0]
        # print(time_zone)
        # I may have to do a more complex mapping. If the database is just listing by a different
        # standard than what I am using, maybe I really do have to flesh out time zones.
        # For now, I could convert to EST; however, I'd really like it to sync up with the database.
        # If only there was a library function that could get this for me.


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
    reminders = relationship("Reminder", order_by=[Reminder.reminder_date, Reminder.reminder_time],
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
