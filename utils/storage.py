import config
import const
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import (
    String,
    Integer,
    Column,
    Boolean,
    create_engine,
    func,
    exc
)

Base = declarative_base()


class UserTable(Base):
    __tablename__ = 'users'

    id = Column('id', Integer(), primary_key=True, autoincrement=True)
    email = Column('email', String(200), unique=True)
    addr = Column('addr', String(200), unique=True)

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', addr='{self.addr}')>"


class TransactionTable(Base):
    __tablename__ = 'transactions'

    id = Column('id', Integer(), primary_key=True, autoincrement=True)
    charge_hosted_url = Column('charge_hosted_url', String(200))
    charge_id = Column('charge_id', String(200))
    charge_code = Column('charge_code', String(200))
    count_images_requested = Column('count_images_requested', Integer())
    item_price = Column('item_price', Integer())
    total_amount = Column('total_amount', Integer())
    status = Column('status', String(200))
    user_id = Column('user_id', Integer())
    images_id_arr = Column('images_id_arr', String(2000), default='')
    blockchain_trans_id = Column('blockchain_trans_id', String(200), default='')

    def __repr__(self):
        return f"<Transaction( \
                      id='{self.id}' \
                      charge_hosted_url='{self.charge_hosted_url}' \
                      charge_id='{self.charge_id}' \
                      charge_code='{self.charge_code}' \
                      count_images_requested='{self.count_images_requested}' \
                      item_price='{self.item_price}' \
                      total_amount='{self.total_amount}' \
                      status='{self.status}' \
                      user_id='{self.user_id}' \
                      images_id_arr='{self.images_id_arr}' \
                      blockchain_trans_id='{self.blockchain_trans_id}' \
                )>"


class ImageTable(Base):
    __tablename__ = 'images'

    id = Column('id', Integer(), primary_key=True, autoincrement=True)
    file_name = Column('file_name', String(200), unique=True)
    is_sent = Column('is_sent', Boolean(), default=False)

    def __repr__(self):
        return f"<Image(id='{self.id}', file_name='{self.file_name}', is_sent='{self.is_sent}')>"


class StorageORM:
    def __init__(self):
        # create connection
        self.engine = create_engine(config.SQLITE_PATH)

        # create tables
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()


class User:
    __session__ = None

    @classmethod
    def set_session(cls, session):
        cls.__session__ = session

    @classmethod
    def get(cls, by='', value=''):
        # TODO: fixed import and except, beautify
        try:
            get_by_dict = {
                'email': cls.__session__.query(UserTable).filter_by(email=value).one,
                'addr': cls.__session__.query(UserTable).filter_by(addr=value).one,
                'id': cls.__session__.query(UserTable).filter_by(id=value).one,
            }

            if by in get_by_dict.keys():
                return get_by_dict[by]()
        except sqlalchemy.exc.NoResultFound:
            pass

        return None

    @classmethod
    def add(cls, addr='', email=''):
        try:
            user = UserTable(addr=addr, email=email)

            cls.__session__.add(user)
            cls.__session__.commit()

            return True
        except exc.IntegrityError:
            cls.__session__.rollback()

        return False


class Transaction:
    __session__ = None

    @classmethod
    def set_session(cls, session):
        cls.__session__ = session

    @classmethod
    def add(cls, charge_hosted_url, charge_id, charge_code, count_images_requested,
            item_price, total_amount, status, user_id):
        try:
            transaction = TransactionTable(
                charge_hosted_url=charge_hosted_url,
                charge_id=charge_id,
                charge_code=charge_code,
                count_images_requested=count_images_requested,
                item_price=item_price,
                total_amount=total_amount,
                status=status,
                user_id=user_id
            )

            cls.__session__.add(transaction)
            cls.__session__.commit()

            return True

        except exc.IntegrityError:
            cls.__session__.rollback()

        return False

    # fixed const CONFIRMED_COINBASE_STATUS
    @classmethod
    def sum_images(cls, user_id=-1):
        try:
            q = cls.__session__ \
                .query(
                    func.sum(TransactionTable.count_images_requested).label('total_count_images_requested'),
                    TransactionTable
                )

            if user_id != -1:
                q = q.filter_by(user_id=user_id)

            q.filter_by(status=const.CONFIRMED_COINBASE_STATUS)

            if user_id != -1:
                q = q.group_by(TransactionTable.user_id)

            return q.scalar()
        except:
            pass

        return None

    @classmethod
    def get(cls, by='', value=''):
        try:
            get_by_dict = {
                'charge_id': cls.__session__.query(TransactionTable).filter_by(charge_id=value).one,
            }

            if by in get_by_dict.keys():
                return get_by_dict[by]()

        except sqlalchemy.exc.NoResultFound:
            pass

        return None

    @classmethod
    def update(cls, charge_id='', column='', value=''):
        try:
            cls.__session__.query(TransactionTable).filter_by(charge_id=charge_id).update({column: value})
            cls.__session__.commit()
            return True
        except sqlalchemy.exc.NoResultFound:
            pass

        return None


class Image:
    __session__ = None

    @classmethod
    def set_session(cls, session):
        cls.__session__ = session

    @classmethod
    def count(cls, is_sent=False):
        return (cls.__session__.query(func.count(ImageTable.id))).filter_by(is_sent=is_sent).scalar()

    @classmethod
    def get(cls, limit=0, is_sent=False):
        try:
            return cls.__session__.query(ImageTable).filter_by(is_sent=is_sent).limit(limit).all()
        except sqlalchemy.exc.NoResultFound:
            pass

        return None

    @classmethod
    def add(cls, file_name='', is_sent=False):
        try:
            image = ImageTable(file_name=file_name, is_sent=is_sent)

            cls.__session__.add(image)
            cls.__session__.commit()

            return True
        except exc.IntegrityError:
            cls.__session__.rollback()

        return False

    @classmethod
    def update(cls, id='', column='', value=''):
        try:
            cls.__session__.query(ImageTable).filter_by(id=id).update({column: value})
            cls.__session__.commit()
            return True
        except sqlalchemy.exc.NoResultFound:
            pass

        return None



