import os

from flask import Flask, render_template, url_for, request, flash, \
    session, redirect, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from db.database import user_view, ads_view
from login import login_data, login_menu, one_adv, craete_token, check_token
from settings import UPLOAD_FOLDER, SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_AS_ASCII'] = False

menu = [
    {'name': 'На главную', 'url': '/'},
    {'name': 'Добавить объявление', 'url': '/form'},
    {'name': 'API', 'url': '/api'},
]


@app.route("/")
@app.route("/ads")
@app.route("/index")
def index():
    print(url_for("index"))
    login = login_menu(session)
    chooose_ads = ''
    if login['login'] and 'ads' in request.args:
        chooose_ads = request.args['ads']
        # if request.args['ads'] == 'my':
    data = login_data(session, chooose_ads)
    return render_template('index.html', title="Главная страница", menu=menu, auth=login, data=data, sign=chooose_ads)


@app.route("/ads/<int:ad_id>", methods=["POST", "GET"])
def ad_id(ad_id):
    print(url_for("ad_id", ad_id=ad_id))
    login = login_menu(session)
    advert = one_adv(session, ad_id)
    if login['login']:
        if 'delete' in request.args:
            if login['username'] == advert['username']:
                ads_view.delete(ad_id)
                flash("Объявление успешно удалено", category='success')
                advert = one_adv(session, ad_id)
                # return redirect(url_for('index'))
            else:
                flash("Не получилось. Вы не можете удалить чужое объявление.", category='error')
        if 'edit' in request.args:
            advert['form'] = True
        if request.method == 'POST':
            if login['username'] == advert['username']:
                if request.form:
                    ads_view.patch(ad_id,
                                    list(dict(request.form).keys())[0],
                                    list(dict(request.form).values())[0]
                                   )
                    advert[list(dict(request.form).keys())[0]] = list(dict(request.form).values())[0]
                    flash("Объявление успешно отредактировано", category='success')
                if request.files:
                    advert['img'] = request.files['img'].filename
                    file = request.files['img']
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], advert['img']))
                    ads_view.patch(ad_id, 'img', advert['img'])
                    flash("Изображение изменено", category='success')
                    advert['img'] = "/static/images/" + request.files['img'].filename
    return render_template('ad.html', title="Главная страница", menu=menu, auth=login, advert=advert)


@app.route("/form", methods=["POST", "GET"])
def form():
    print(url_for("form"))
    login = login_menu(session)
    if request.method == "POST":
        advert = dict(request.form)
        advert['img'] = request.files['img'].filename
        if len(advert['title']) > 2 and len(advert['content']) > 5:
            if login['login']:
                user = user_view.get(dict(arg='user_info', username=login['username']))
                advert['firstname'] = user.firstname
                advert['user_id'] = user.id
            else:
                if len(advert['firstname']) > 2:
                    advert['user_id'] = 2
                else:
                    flash("Не получилось. Введите настоящее имя.", category='error')
            if advert['img']:
                file = request.files['img']
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], advert['img']))
            else:
                advert['img'] = 'no-photo.jpg'
            flash("Ваше объявление добавлено", category='success')
            ads_view.post(advert)
        else:
            flash("Не получилось. Поля заполнены не корректно.", category='error')
    advert = 'Заполните все поля формы'
    return render_template('form.html', title="Новое объявление", menu=menu, auth=login, advert=advert)


@app.route("/registr", methods=["POST", "GET"])
def registr():
    print(url_for("registr"))
    login = login_menu(session)
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    if request.method == "POST":
        user_data = dict(request.form)
        check = user_view.get({'arg': 'check', 'username': user_data['username'], 'email': user_data['email']})
        if len(user_data['username']) < 2 or len(user_data['firstname']) < 2 or len(user_data['password']) < 6:
            flash('Заполните все обязательные поля. Длина пароля должна быть не менее 6 символов', category='error')
            return render_template('registr.html', title="Страница регистрации", menu=menu, auth=login)
        if user_data['password'] != user_data['password2']:
            flash('Пароли не совпадают', category='error')
            return render_template('registr.html', title="Страница регистрации", menu=menu, auth=login)
        if user_data['email']:
            if '@' not in list(user_data['email']) and '.' not in list(user_data['email']):
                flash('Неверно введен email', category='error')
                return render_template('registr.html', title="Страница регистрации", menu=menu, auth=login)
        if check[0]:
            flash(check[1], category='error')
        else:
            user_data['password'] = generate_password_hash(user_data['password'])
            flash("Поздравляем! Вы зарегистрированы.", category='success')
            user_view.post(user_data)
            session['userLogged'] = user_data['username'].capitalize()
            return redirect(url_for('profile', username=session['userLogged']))
    if request.method == "GET" and request.args:
        user_data = {'username': request.args['username'], 'firstname': request.args['firstname'].capitalize(),
                     'lastname': request.args['lastname'].capitalize(), 'email': request.args['email'],
                     'password': request.args['password']}
        user_view.post(user_data)
        return redirect(url_for('profile', user_data=user_data))
    return render_template('registr.html', title="Страница регистрации", menu=menu, auth=login)


@app.route("/auth", methods=["POST", "GET"])
def auth():
    print(url_for("auth"))
    login = login_menu(session)
    if login['login']:
        return redirect(url_for('profile', username=session['userLogged']))
    if request.method == "POST":
        check = user_view.get({'arg': 'check', 'username': request.form['username'].capitalize(), 'email': '-'})
        if check[0]:
            user = user_view.get({'arg': 'user_info', 'username': request.form['username'].capitalize()})
            if check_password_hash(user.password, request.form['password']):
                session['userLogged'] = request.form['username'].capitalize()
                return redirect(url_for('profile', username=login['username']))
            else:
                flash("Не верно введен пароль", category='error')
        else:
            flash("Пользователь с таким именем не зарегистрирован", category='error')
    return render_template('auth.html', title="Авторизация", menu=menu, auth=login)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    print(url_for("profile"))
    login = login_menu(session)
    if not login['login']:
        return redirect(url_for('auth'))
    user_info = user_view.get(dict(arg='user_info', username=login['username']))
    if 'change' in request.args:
        change_user_data = request.args
        if change_user_data['change'] == 'password':
            pass
        else:
            user_view.patch(login['username'], change_user_data['change'], change_user_data['value'])
            flash("Произведена замена в учетных данных.", category='success')
            user_info= user_view.get(dict(arg='user_info', username=login['username']))
    if 'delete' in request.args:
        login['delete'] = 1
        if 'confirm_del' in request.args:
            del session['userLogged']
            user_view.delete(user_info.id)
            flash("Профиль удален.", category='success')
            return redirect(url_for('profile'))
    if request.method == "POST" and 'psw' in request.form:
        psw = generate_password_hash(request.form['psw'])
        return render_template('profile.html', title="Авторизация", text_link="Профиль", \
                               menu=menu, auth=login, user=user_info, psw=psw)
    if request.method == "POST" and 'password2' in request.form:
        if check_password_hash(request.form['password'], request.form['password2']):
            user_view.patch(login['username'], 'password', request.form['password'])
            flash("Пароль успешно изменен.", category='success')
    return render_template('profile.html', title="Авторизация", text_link="Профиль",\
                           menu=menu, auth=login, user=user_info)

@app.route("/exit", methods=["GET"])
def session_exit():
    if 'userLogged' in session:
        print(session['userLogged'])
        del session['userLogged']
    print(url_for("session_exit"))
    return redirect(url_for('profile'))


@app.route("/api/0")
def api_0():
    login = login_menu(session)
    print(url_for("api_0"))
    return jsonify({'status': 'ok', })


@app.errorhandler(404)
def no_page(error):
    login = login_menu(session)
    return render_template('404.html', title="Страница не найдена", menu=menu, auth=login), 404


@app.route("/api", methods=["GET"])
def api():
    print(url_for("api"))
    login = login_menu(session)
    token = {}
    if 'get_token' in request.args:
        token['token'] = craete_token(session, app.config['SECRET_KEY'])
        if login['login']:
            token["text"] = 'Скопируйте Ваш токен'
        headers = request.headers
        if 'login' in headers and 'password' in headers:
            if user_view.get({'arg': 'check', 'username': headers['login']})[0]:
                user = user_view.get({'arg': 'user_info', 'username': headers['login'].capitalize()})
                if check_password_hash(user.password, headers['password']):
                    token['token'] = craete_token({'userLogged': headers['login']}, app.config['SECRET_KEY'])
                    return {'token': token['token']}
                else:
                    return {'status': 'Неверный пароль'}
            else:
                return {'status': 'Такого логина нет'}
    return render_template('api.html', title="API", menu=menu, auth=login, get_token=token)


@app.route("/api/ads", methods=["POST", "GET"])
def api_ads():
    print(url_for("api_ads"))
    if request.method == 'POST':
        if 'auth' in request.headers:
            json_advert = request.json
            if json_advert['title'] and json_advert['content']:
                user = user_view.get({'arg': 'user_info',
                                      'username': check_token(request.headers['auth'], app.config['SECRET_KEY'])[
                                          'username']
                                      })
                ads_view.post({'title': json_advert['title'],
                               'content': json_advert['content'],
                               'user_id': user.id,
                               'firstname': user.firstname,
                               'img': 'no-photo.jpg',
                               })
                return {'status': 'Отлично! Вы добавили новое объявление'}
            else:
                return {'Что-то Вы забыли. Попробуйте передать еще раз все необходимые строки'}
        else:
            return {'status': 'Что Вы делаете? Вы же не авторизованы. Сначала получите токен и введите его в headers'}
    data = login_data(session, '')
    return jsonify(data)

@app.route("/api/ads/<int:ad_id>", methods=["GET", "DELETE", "PATCH"])
def api_ads_id(ad_id):
    print(url_for("api_ads_id", ad_id=ad_id))
    data = one_adv(session, ad_id)
    if request.method == 'DELETE':
        if 'auth' in request.headers:
            if data['username'] == check_token(request.headers['auth'], app.config['SECRET_KEY'])['username']:
                ads_view.delete(ad_id)
                return {'status': 'Ура, сработало! Вы удалили свое объявление'}
            else:
                return {'status': 'Не получилось. Это объявление Вам не принадлежит'}
    if request.method == 'PATCH':
        if 'auth' in request.headers:
            if data['username'] == check_token(request.headers['auth'], app.config['SECRET_KEY'])['username']:
                if 'title' in request.json:
                    ads_view.patch(ad_id, 'title', request.json['title'])
                elif 'content' in request.json:
                    ads_view.patch(ad_id, 'content', request.json['content'])
                else:
                    return {'status': 'Похоже Вы что-то не то ввели'}
                return {'status': 'Отличная работа! Объявление изменено'}
            else:
                return {'status': 'Не получилось. Это объявление Вам не принадлежит'}
        return {'status': 'Что Вы делаете? Вы же не авторизованы. Сначала получите токен и введите его в headers'}
    return jsonify(data)



if __name__ == "__main__":
    app.run(debug=True)