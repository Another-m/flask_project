from datetime import datetime, timedelta

from db.database import ads_view
import jwt


def login_menu(session):
    if 'userLogged' in session:
        username=session['userLogged']
        login = True
        auth_menu = {'info': f"Вы вошли как: {session['userLogged']}", 'menu': [
            {'name': "Профиль", 'url': '/profile'},
            {'name': 'Выход', 'url': '/exit'},
        ]}
    else:
        username = ''
        login = False
        auth_menu = {'info': "Вы не авторизованы", 'menu': [
            {'name': 'Вход', 'url': '/auth'},
            {'name': 'Регистрация', 'url': '/registr'},
        ]}
    return dict(login=login, auth_menu=auth_menu, username=username)


def login_data(session, choose_ads):
    data = []
    login = None
    all_ads = ads_view.get(0)
    if 'userLogged' in session:
        login = session['userLogged']
    for i in all_ads:
        try: username = i.owner.username
        except: username = 'Гость'
        if choose_ads == 'my':
            if username != login and login is not None:
                continue
        data.append({'id': i.id,
                     'firstname': str(i.firstname),
                     'username': str(username),
                     'title': str(i.title),
                     'content': str(i.description),
                     'img': i.image_link,
                     'created_at': i.created_at.strftime("%d-%m-%Y %H:%M:%S")
                     })
    return data

def one_adv(session, ad_id):
    data = ads_view.get(ad_id)
    if not data:
        advert = {'id': None, 'title': 'Объявления не существует'}
    else:
        try: username = data.owner.username
        except: username = 'Гость'
        advert = {'id': data.id,
                  'firstname': data.firstname,
                  'username': username,
                  'title': data.title,
                  'content': data.description,
                  'img': data.image_link,
                  'created_at': data.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                  'owner': False
                  }
        if 'userLogged' in session and username == session['userLogged']:
            advert['owner'] = True
    return advert

def craete_token(session, secr_key):
    if 'userLogged' in session:
        username = session['userLogged']
    else:
        return 'Вы не авторизованы!'
    token = jwt.encode(
        {'username': username, 'exp': datetime.utcnow() + timedelta(days=30)},
        secr_key)
    return token



def check_token(token, secr_key):
    try:
        data = jwt.decode(token, secr_key, options={"verify_signature": False})
    except:
        data = "Не верный токен"
    return data

