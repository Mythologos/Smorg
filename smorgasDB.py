import functools
import secretbord
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, ForeignKey
from sqlalchemy import BigInteger, DateTime, SmallInteger, String
import time

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


def session_method(decorated_function):
    @functools.wraps(decorated_function)
    def session_decorator(*args, **kwargs):
        method_session = Session()
        session_value = decorated_function(method_session, *args, **kwargs)
        method_session.close()
        return session_value
    return session_decorator


class Quote(Base):
    __tablename__ = 'quotes'

    # Attributes:
    author = Column(String(100), nullable=True)
    guild_id = Column(BigInteger, ForeignKey('guilds.guild_id'), nullable=False)
    quote_id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False)
    text = Column(String, nullable=False)
    # created_at = Column(DateTime, default=time.time(), nullable=False)
    # last_updated_at = Column(DateTime, default=time.time(), nullable=False, onupdate=time.time()

    # Relationships:
    guild = relationship("Guild", back_populates="quotes")

    def __repr__(self):
        return '<Guild(author: {0}, guild_id: {1}, quote_id: {2}, text: {3}>'\
            .format(self.author, self.guild_id, self.quote_id, self.text)


class Guild(Base):
    __tablename__ = 'guilds'

    # Attributes:
    guild_id = Column(BigInteger, primary_key=True, nullable=False)
    quotation_channel_id = Column(BigInteger, unique=True, nullable=False)
    # created_at = Column(DateTime, default=time.time(), nullable=False)
    # last_updated_at = Column(DateTime, default=time.time(), nullable=False, onupdate=time.time()

    # Relationships:
    quotes = relationship("Quote", order_by=Quote.quote_id, back_populates="guild")

    def __repr__(self):
        return '<Guild(guild_id: {0}, quotation_channel_id: {1}>'\
            .format(self.guild_id, self.quotation_channel_id)


def reset_database():
    Base.metadata.drop_all()
    Base.metadata.create_all()


@session_method
def create_quote_with(method_session, g_id, quote, auth=None):
    new_quote = Quote(author=auth, guild_id=g_id, text=quote)
    method_session.add(new_quote)
    method_session.commit()


@session_method
def get_random_quote_by(method_session, g_id, q_number):
    quote = method_session.query(Quote.author, Quote.text).filter_by(guild_id=g_id)[q_number]
    return quote


@session_method
def count_quotes(method_session, g_id):
    count = method_session.query(Quote).filter_by(guild_id=g_id).count()
    return count


@session_method
def has_assigned_channel_by(method_session, g_id):
    assigned_channel = method_session.query(Guild.quotation_channel_id).filter_by(guild_id=g_id).first()
    has_assigned_channel = assigned_channel is not None
    return has_assigned_channel


@session_method
def get_assigned_channel_by(method_session, g_id):
    assigned_channel = method_session.query(Guild.quotation_channel_id).filter_by(guild_id=g_id).first()
    return assigned_channel[0]


@session_method
def create_guild_with(method_session, g_id, c_id):
    new_guild = Guild(guild_id=g_id, quotation_channel_id=c_id)
    method_session.add(new_guild)
    method_session.commit()


@session_method
def update_assigned_channel(method_session, g_id, c_id):
    method_session.query(Guild)\
                  .filter_by(guild_id=g_id)\
                  .update({"quotation_channel_id": c_id})
    method_session.commit()
