# TODO: MODULAR DOCUMENTATION
# TODO: handle deleted channels case for various tables here
# TODO: add DB field to control the prefix of the bot.


import secretbord
import sqlalchemy
from functools import wraps
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, ForeignKey
from sqlalchemy import BigInteger, Date, DateTime, SmallInteger, String, Time

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


# TODO: describe this as a mixin.
class BaseAddition:
    @classmethod
    def session_method(cls, decorated_function):
        """
        Decorator; automatically sets up and closes sessions for database connections.
        :param decorated_function: a function that requires a session.
        :return: a function with the built-in capability of opening and closing a session.
        """
        @wraps(decorated_function)
        def session_decorator(*args, **kwargs):
            method_session = Session()
            session_value = decorated_function(method_session, *args, **kwargs)
            method_session.close()
            return session_value
        return session_decorator

    @staticmethod
    def reset_database():
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
        return '<Guild(author: {0}, guild_id: {1}, quote_id: {2}, text: {3}, ' + \
               'created_at: {4}, last_updated_at: {5}>'\
            .format(self.author, self.guild_id, self.quote_id, self.text,
                    self.created_at, self.last_updated_at)

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
    def create_quote_with(method_session, g_id, quote, auth):
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
    def __repr__(self):
        return '<Guild(guild_id: {0}, tag: {1}, tag_text: {2}, reminder_date: {3}, ' + \
            'reminder_time: {4} created_at: {5}, last_updated_at: {6}>'\
            .format(self.guild_id, self.tag, self.tag_text, self.reminder_date, self.reminder_time,
                    self.created_at, self.last_updated_at)

    @staticmethod
    @BaseAddition.session_method
    def create_reminder_with(method_session, g_id, tag, tag_text, date, time):
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
        return '<Guild(guild_id: {0}, gamble_channel_id: {1}, guild_prefix: {2}, quotation_channel_id: {3}, ' \
               'reminder_channel_id: {3}' + 'created_at: {4}, last_updated_at: {5}>' \
            .format(self.guild_id,self.gamble_channel_id, self.guild_prefix, self.quotation_channel_id,
                    self.reminder_channel_id, self.created_at, self.last_updated_at)

    # Queries:
    @staticmethod
    @BaseAddition.session_method
    def get_quotation_channel_by(method_session, g_id):
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
    def exists_with(method_session, g_id):
        """
        This method determines whether a Guild has channels assigned to it.
        :param method_session: a Session database connection.
        :param g_id: a Discord Guild ID (Integer).
        :return: a Boolean of whether a Guild has a channel quotation to it according to the database.
        """
        guild_id = method_session.query(Guild.guild_id).filter_by(guild_id=g_id).first()
        guild_existence = guild_id is not None
        return guild_existence

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
        new_guild = Guild(guild_id=g_id, quotation_channel_id=c_id, reminder_channel_id=c_id)
        method_session.add(new_guild)
        method_session.commit()

    @staticmethod
    @BaseAddition.session_method
    def update_quotation_channel(method_session, g_id, c_id):
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
    def get_reminder_channel_by(method_session, g_id):
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
    def update_reminder_channel(method_session, g_id, c_id):
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
    def get_gamble_channel_by(method_session, g_id):
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
    def update_gamble_channel(method_session, g_id, c_id):
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
    def get_prefix(method_session, bot, message):
        g_id: int = message.channel.guild.id
        guild_prefix = method_session.query(Guild.guild_prefix).filter_by(guild_id=g_id).first()
        return guild_prefix[0]

    @staticmethod
    @BaseAddition.session_method
    def update_prefix(method_session, g_id, new_prefix):
        method_session.query(Guild) \
                      .filter_by(guild_id=g_id) \
                      .update({"guild_prefix": new_prefix})
        method_session.commit()
