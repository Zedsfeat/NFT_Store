from abc import ABC, abstractmethod

import bcrypt
import psycopg2
from flask_login import UserMixin


class DataBase(ABC):
    con = psycopg2.connect(
        dbname='NFTPictureStore',
        user='postgres',
        password='importPower1q2w3e4r'
    )

    @abstractmethod
    def __init__(self, *args):
        self.cur = self.con.cursor()

    @classmethod
    def get_all(cls, name):
        try:
            cur = cls.con.cursor()
            cur.execute(f"SELECT * FROM {name};")
            return cls.prepare_data(cur.fetchall())

        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def prepare_data(cls, list_of_rows):
        list_of_objects = []
        for row in list_of_rows:
            list_of_objects.append(cls(*row))
        return list_of_objects

    @abstractmethod
    def save(self):
        pass

    def update(self, name, keys, values):
        try:
            keys = keys.replace(' ', ', ')
            request = f"UPDATE {name} SET ({keys}) = (" + "%s, " * len(values)
            request = request[:-2] + f") WHERE id = {self.id}"
            self.cur.execute(request, values)
            self.con.commit()

        except Exception as ex:
            print(ex)
            return False


class GetByIdMixin:
    @classmethod
    def get_by_id(cls, obj_id, name):
        try:
            cur = cls.con.cursor()
            cur.execute(f"SELECT * FROM {name} WHERE id = {obj_id};")
            obj = cls.prepare_data(cur.fetchall())
            if len(obj):
                return obj[0]
            return False

        except Exception as ex:
            print(ex)
            return False

class GetByUserAdvertMixin:
    @classmethod
    def get_by_user_advert(cls, name, user_id, advert_id):
        try:
            cur = cls.con.cursor()
            cur.execute(f"SELECT * FROM {name} WHERE user_id = {user_id} AND advert_id = {advert_id};")
            obj = cls.prepare_data(cur.fetchall())
            if len(obj):
                return obj[0]
            return False

        except Exception as ex:
            print(ex)
            return False

class GetByUserIdMixin:
    @classmethod
    def get_by_user_id(cls, user_id, name):
        try:
            cur = cls.con.cursor()
            cur.execute(f"SELECT * FROM {name} WHERE user_id = {user_id};")
            return cls.prepare_data(cur.fetchall())

        except Exception as ex:
            print(ex)
            return False

class DeleteFromUserAdvert:
    def delete(self, name):
        try:
            self.cur.execute(f"DELETE FROM {name} WHERE user_id = {self.user_id} AND advert_id = {self.advert_id}")
            self.con.commit()

        except Exception as ex:
            print(ex)
            return False


class User(DataBase, UserMixin, GetByIdMixin):
    def __init__(self, email, password, name=None, image_url=None, admin_status=False, id=None, registration_date=None):
        super().__init__()
        self.email = email
        if id is None:
            self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).hex()
        else:
            self.password = password
        if name:
            self.name = name
        else:
            self.name = email.split('@')[0]
        self.image_url = image_url
        self.admin_status = admin_status
        self.id = id
        self.registration_date = registration_date

    @classmethod
    def get_by_email(cls, email):
        try:
            cur = cls.con.cursor()
            cur.execute(f"SELECT * FROM users WHERE email = '{email}';")
            obj = cls.prepare_data(cur.fetchall())
            if len(obj):
                return obj[0]
            return False

        except Exception as ex:
            print(ex)
            return False

    def save(self):
        try:
            data = [self.email, self.password, self.name, self.image_url]
            self.cur.execute("INSERT INTO users VALUES (%s, %s, %s, %s);", data)
            self.con.commit()
            user = User.get_all('users')[-1]
            self.id = user.id
            self.registration_date = user.registration_date

        except Exception as ex:
            print(ex)
            return False

    def delete(self):
        try:
            self.cur.execute(f"DELETE FROM users WHERE id = {self.id}")
            self.con.commit()

        except Exception as ex:
            print(ex)
            return False

    @staticmethod
    def check_password(hash_password, password):
        return bcrypt.checkpw(password.encode(), bytes.fromhex(hash_password))


class Advert(DataBase, GetByIdMixin):
    def __init__(self, title, description, category, price, image_url, user_id, id=None, is_active=True):
        super().__init__()
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.image_url = image_url
        self.user_id = user_id
        self.id = id
        self.is_active = is_active

    @classmethod
    def get_all_by_filters(cls, **kwargs):
        request = f"SELECT * FROM adverts"
        if kwargs:
            request += " WHERE "
            for key, value in kwargs.items():

                if key == 'id':
                    request += f"id = {value} AND "
                elif key == 'is_active':
                    if value:
                        request += f"{key} = true AND "
                    else:
                        request += f"{key} = false AND "

                elif value == "not null":
                    request += f"{key} IS NOT NULL AND "
                elif key == 'category' and value:
                    request += "category = %s AND "
                elif key == 'search' and value:
                    request += "(UPPER(title) LIKE UPPER(%s) OR UPPER(description) LIKE UPPER(%s)) AND "
                else:
                    print(f"Not expected argument '{key}' with value '{value}'")

            request = request[:-5] + ';'
        try:
            cur = cls.con.cursor()
            if kwargs.get('category') and kwargs.get('search'): # Проверяем есть ли
                cur.execute(request, [kwargs['category']] + ['%' + kwargs['search'] + '%'] * 2) # Делаем запрос в бд
            elif kwargs.get('category'):
                cur.execute(request, [kwargs['category']])
            elif kwargs.get('search'):
                cur.execute(request, ['%' + kwargs['search'] + '%'] * 2)
            else:
                cur.execute(request) # Выводим все advert
            return cls.prepare_data(cur.fetchall()) # Возвращаем кортежи запросов

        except Exception as ex:
            print(ex)
            return False

    def save(self):
        try:
            data = [self.title, self.description, self.category, self.price, self.image_url, self.user_id]
            self.cur.execute("INSERT INTO adverts VALUES  (%s, %s, %s, %s, %s, %s);", data)
            self.con.commit()
            advert = Advert.get_all('adverts')[-1]
            self.id = advert.id
            self.is_active = advert.is_active

        except Exception as ex:
            print(ex)
            return False

    def delete(self):
        try:
            self.cur.execute(f"DELETE FROM adverts WHERE id = {self.id}")
            self.con.commit()

        except Exception as ex:
            print(ex)
            return False

    def hidden(self):
        try:
            self.cur.execute(f"UPDATE adverts SET is_active = false WHERE id = {self.id}")
            self.con.commit()

        except Exception as ex:
            print(ex)
            return False


class Order(DataBase, GetByIdMixin, GetByUserIdMixin):
    def __init__(self, summa, user_id, id=None, created_date=None):
        super().__init__()
        self.summa = summa
        self.user_id = user_id
        self.id = id
        self.created_date = created_date

    def save(self):
        try:
            self.cur.execute("INSERT INTO orders VALUES (%s, %s);", [self.summa, self.user_id])
            self.con.commit()
            order = Order.get_all('orders')[-1]
            self.id = order.id
            self.created_date = order.created_date

        except Exception as ex:
            print(ex)
            return False


class Purchase(DataBase):
    def __init__(self, advert_id, order_id):
        super().__init__()
        self.advert_id = advert_id
        self.order_id = order_id

    def save(self):
        try:
            self.cur.execute("INSERT INTO purchases VALUES (%s, %s);", [self.advert_id, self.order_id])
            self.con.commit()

        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def get_by_order_id(cls, order_id):
        try:
            cur = cls.con.cursor()
            cur.execute(f"SELECT * FROM purchases WHERE order_id = {order_id};")
            return cls.prepare_data(cur.fetchall())

        except Exception as ex:
            print(ex)
            return False


class Favorite(DataBase, GetByUserAdvertMixin, GetByUserIdMixin, DeleteFromUserAdvert):
    def __init__(self, user_id, advert_id):
        super().__init__()
        self.user_id = user_id
        self.advert_id = advert_id

    def save(self):
        try:
            self.cur.execute("INSERT INTO favorites VALUES (%s, %s);", [self.user_id, self.advert_id])
            self.con.commit()

        except Exception as ex:
            print(ex)
            return False


class Cart(DataBase, GetByUserAdvertMixin, GetByUserIdMixin, DeleteFromUserAdvert):
    def __init__(self, user_id, advert_id):
        super().__init__()
        self.user_id = user_id
        self.advert_id = advert_id

    def save(self):
        try:
            self.cur.execute("INSERT INTO cart VALUES (%s, %s);", [self.user_id, self.advert_id])
            self.con.commit()

        except Exception as ex:
            print(ex)
            return False

