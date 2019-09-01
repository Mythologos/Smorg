# TODO: MODULAR DOCUMENTATION

import functools
import secretbord
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, ForeignKey
from sqlalchemy import BigInteger, DateTime, SmallInteger, String

engine = sqlalchemy.create_engine(secretbord.database + '+' +
                                  secretbord.dialect + '://' +
                                  secretbord.username + ':' +
                                  secretbord.password + '@' +
                                  secretbord.host + ':' +
                                  secretbord.port + '/' +
                                  secretbord.database_name,
                                  connect_args=secretbord.options, echo=True)

Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


def reset_database():
    """
    This method resets the database down to the structure based upon the classes described above.
    :return: None.
    """
    Base.metadata.drop_all()
    Base.metadata.create_all()


# TODO: describe this as a mixin.
class BaseAddition:
    @classmethod
    def session_method(cls, decorated_function):
        """
        Decorator; automatically sets up and closes sessions for database connections.
        :param decorated_function: a function that requires a session.
        :return: a function with the built-in capability of opening and closing a session.
        """
        @functools.wraps(decorated_function)
        def session_decorator(*args, **kwargs):
            method_session = Session()
            session_value = decorated_function(method_session, *args, **kwargs)
            method_session.close()
            return session_value
        return session_decorator


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
        return '<Guild(author: {0}, guild_id: {1}, quote_id: {2}, text: {3}>'\
            .format(self.author, self.guild_id, self.quote_id, self.text)

    # Queries:
    @staticmethod
    @BaseAddition.session_method
    def count_quotes(method_session, g_id):
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
    def create_quote_with(method_session, g_id, quote, auth=None):
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
    def get_random_quote_by(method_session, g_id, q_number):
        """
        This method retrieves a random quote from a given server from the database.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param q_number: a random number less than the maximum number of quotes that a server has.
        :return: a Quote's author and text, in that order, in a Tuple.
        """
        quote = method_session.query(Quote.author, Quote.text).filter_by(guild_id=g_id)[q_number]
        return quote


class Guild(Base, BaseAddition):
    """
    This class represents a Discord server, called a Guild.
    """
    __tablename__ = 'guilds'

    # Attributes:
    guild_id = Column(BigInteger, primary_key=True, nullable=False)
    quotation_channel_id = Column(BigInteger, unique=True, nullable=False)
    created_at = Column(DateTime, default=sqlalchemy.sql.func.now(), nullable=False)
    last_updated_at = Column(DateTime, default=sqlalchemy.sql.func.now(),
                             nullable=False, onupdate=sqlalchemy.sql.func.now())

    # Relationships:
    quotes = relationship("Quote", order_by=Quote.quote_id, back_populates="guild")

    # Methods:
    def __repr__(self):
        return '<Guild(guild_id: {0}, quotation_channel_id: {1}>'\
            .format(self.guild_id, self.quotation_channel_id)

    # Queries:
    @staticmethod
    @BaseAddition.session_method
    def get_assigned_channel_by(method_session, g_id):
        """
        This method retrieves the assigned channel for a given Guild.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :return: a channel ID (Integer).
        """
        assigned_channel = method_session.query(Guild.quotation_channel_id).filter_by(guild_id=g_id).first()
        return assigned_channel[0]

    @staticmethod
    @BaseAddition.session_method
    def has_assigned_channel_by(method_session, g_id):
        """
        This method determines whether a Guild has an assigned channel for embedding quotes.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :return: a Boolean of whether a Guild has a channel assigned to it according to the database.
        """
        assigned_channel = method_session.query(Guild.quotation_channel_id).filter_by(guild_id=g_id).first()
        has_assigned_channel = assigned_channel is not None
        return has_assigned_channel

    @staticmethod
    @BaseAddition.session_method
    def create_guild_with(method_session, g_id, c_id):
        """
        This method creates a Guild and stores it in the database.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param c_id: a Discord Channel ID (Integer).
        :return: None.
        """
        new_guild = Guild(guild_id=g_id, quotation_channel_id=c_id)
        method_session.add(new_guild)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def update_assigned_channel(method_session, g_id, c_id):
        """
        This method retrieves a Guild and updates its assigned channel.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :param c_id: a Discord Channel ID (Integer).
        :return: None.
        """
        method_session.query(Guild)\
                      .filter_by(guild_id=g_id)\
                      .update({"quotation_channel_id": c_id})
        method_session.commit()
