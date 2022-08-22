from flask.views import MethodView
from sqlalchemy import Column, Integer, String, DateTime, func, create_engine, \
    ForeignKey, desc, exists
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from settings import DATABASE, DRIVER, OWNER, PASSWORD, HOST, PORT, NAME

engine = create_engine(f"{DATABASE}+{DRIVER}://{OWNER}:{PASSWORD}@{HOST}:{PORT}/{NAME}", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Ads(Base):

    __tablename__ = 'ads'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), default=2)
    firstname = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_link = Column(String, default='/static/images/no-photo.jpg')
    created_at = Column(DateTime, server_default=func.now())
    owner = relationship(User, backref="users", lazy='subquery')


Base.metadata.create_all(engine)


class UserView(MethodView):

    def get(self, request):
        with Session() as session:
            if request['arg'] == 'check':
                check_un = session.query(exists().where(User.username == request['username'].capitalize())).scalar()
                if check_un == True: return [1, 'Пользователь с таким именем уже существует']
                check_em = session.query(exists().where(User.email == request['email'].lower())).scalar()
                if check_em == True and request['email'] != "": return [1, 'Пользователь с таким e-mail адресом уже зарегистрирован']
                return [0, 'OK']
            elif request['arg'] == 'user_info':
                user = session.query(User).filter(User.username == request['username']).one()
                return user
            elif request['arg'] == 'all_users':
                user = session.query(User).all()
                return user


    def post(self, user_data):
        with Session() as session:
            if user_data['email']:
                user = User(username=user_data['username'].capitalize(),
                             firstname=user_data['firstname'].capitalize(),
                             lastname=user_data['lastname'].capitalize(),
                             email=user_data['email'].lower(),
                             password=user_data['password']
                             )
            else:
                user = User(username=user_data['username'].capitalize(),
                             firstname=user_data['firstname'].capitalize(),
                             lastname=user_data['lastname'].capitalize(),
                             password=user_data['password']
                             )
            session.add(user)
            session.commit()


    def patch(self, username: str, key: str, value):
        with Session() as session:
            user = session.query(User).filter(User.username == username).one()
            if key == 'firstname':
                user.firstname = value
            if key == 'lastname':
                user.lastname = value
            if key == 'email':
                user.email = value
            if key == 'password':
                user.password = value
            session.add(user)
            session.commit()


    def delete(self, uid):
        with Session() as session:
            advert = session.query(User).get(uid)
            session.delete(advert)
            session.commit()


class AdsView(MethodView):

    def get(self, ad_id):
        with Session() as session:
            if ad_id == 0:
                all_ads = session.query(Ads).order_by(desc(Ads.created_at))
                return all_ads
            else:
                try:
                    ad = session.query(Ads).get(ad_id)
                except: ad = None
                return ad

    def post(self, advert):
        with Session() as session:
            new_advert = Ads(user_id=advert['user_id'],
                             firstname=advert['firstname'].capitalize(),
                             title=advert['title'].capitalize(),
                             description=advert['content'],
                             image_link=f"/static/images/{advert['img']}"
            )
            session.add(new_advert)
            session.commit()

    def patch(self, ad_id: int, key, value):
        with Session() as session:
            user = session.query(Ads).filter(Ads.id == ad_id).one()
            if key == 'title':
                user.title = value
            if key == 'img':
                user.image_link = f"/static/images/{value}"
            if key == 'content':
                user.description = value
            session.add(user)
            session.commit()

    def delete(self, adv_id):
        with Session() as session:
            advert = session.query(Ads).get(adv_id)
            session.delete(advert)
            session.commit()



user_view = UserView()
ads_view = AdsView()