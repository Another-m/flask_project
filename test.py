from werkzeug.security import generate_password_hash

from db.database import user_view, ads_view
import requests

  # Смена пароля пользователя
# password = generate_password_hash('123')
# print(user_view.patch('Admin', 'password', password))

  # Смена других учетных данных
# print(user_view.patch('Another, 'email', 'another@another.ru'))

  # Информация обо всех пользователях
users = user_view.get({'arg': 'all_users'})
for i in users:
    # print(i.id)
    # print(i.username)
    # print(i.firstname)
    # print(i.lastname)
    # print(i.email)
    # print(i.password)
    print(i.id, i.username, i.firstname, i.lastname, i.email, i.password, )

  # Удаление объявлений
print([i.id for i in ads_view.get(0)])
# del_ads = ads_view.delete(1)

  # Запрос отдельного объявления
# ad = ads_view.get(26)
# print(ad.id)
# print(ad.firstname)
# print(ad.customer.username)


   # API запросы
HOST = 'http://localhost:5000/api'# + "/ads" + "/45"
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjYzNzU5ODE5fQ.XNTAcGKZMuOKEzZuYOZXzr_iqpMq2K-4noH76d9Ae0Y'
params = {'get_token': 1, }
headers = {'Auth': TOKEN}
# headers = {'login': 'admin', 'password': '123'}

response = requests.get(url=HOST,
                        headers=headers,
                        # params=params
                        )

# response = requests.post(url=HOST,
#                         headers=headers,
#                         # params=params
#                         json={'title': 'Объявление JSON', 'content': 'Объявление JSON тестовое'}
#                         )

# response = requests.patch(url=HOST,
#                         headers=headers,
#                         # params=params
#                         json={'title': 'Объявление тестовое'}
#                         )

# response = requests.delete(url=HOST,
#                         headers=headers,
#                         # params=params
#                         # json={'content': ''}
#                         )

print(response.text)
