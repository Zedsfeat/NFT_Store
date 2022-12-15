import bcrypt
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from orm import User, Advert, Order, Purchase, Favorite, Cart

app = Flask(__name__)
app.config['SECRET_KEY'] = "asdasdasd12edasdasd1easdeqwe"
login_manager = LoginManager(app)

categories = [
    'Bored Ape Yacht Club',
    'CryptoPunks',
    'Mutant Ape Yacht Club',
    'Otherdeed for Otherside',
    'Art Blocks',
    'CLONE X - X TAKASHI MURAKAMI',
    'Azuki',
    'Moonbirds'
]

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id, 'users')


@app.route('/')
def home():
    return redirect('/auth')

@app.route('/auth')
def auth():
    return render_template('auth.html')


@app.route('/adverts', methods=['GET'])
@login_required
def main():
    category = request.args.get('category')
    search = request.args.get('search')
    filters = {
        'user_id': 'not null',
        'is_active': True,
        'category': category,
        'search': search
    }

    adverts = Advert.get_all_by_filters(**filters)

    if not search:
        search = ''
    context = {
        'adverts': adverts,
        'search': search,
        'categories': categories
    }
    return render_template('main.html', **context)


@app.route('/advert/<int:page_id>')
@login_required
def advert(page_id):
    adv = Advert.get_by_id(page_id, 'adverts')
    if adv.user_id:
        owner = User.get_by_id(adv.user_id, 'users').name
    else:
        owner = '<unknown>'
    context = {
        'advert': adv,
        'owner': owner,
        'categories': categories
    }

    if Cart.get_by_user_advert('cart', current_user.id, page_id):
        context['in_cart'] = True
    else:
        context['in_cart'] = False

    if Favorite.get_by_user_advert('favorites', current_user.id, page_id):
        context['in_favorite'] = True
    else:
        context['in_favorite'] = False

    return render_template('advert.html', **context)


@app.route('/register', methods=['GET', 'POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    image_url = request.form.get('image_url')

    context = {'categories': categories}
    if name:
        context['name'] = name
    else:
        context['name'] = ''

    if email:
        context['email'] = email
    else:
        context['email'] = ''

    if image_url:
        context['image_url'] = image_url
    else:
        context['image_url'] = ''

    if request.method == 'POST':
        password = request.form.get('pwd')
        password2 = request.form.get('pwd2')

        if email and password and password2:
            if password != password2:
                flash('Passwords are not equal!')
            else:
                if User.get_by_email(email):
                    flash('Have user with this email')
                else:
                    user = User(email, password, name, image_url)
                    user.save()

                    return redirect(url_for('login'))

        else:
            flash('Please, fill all fields! However, you can leave the name field empty')

    return render_template('register.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    if request.method == 'POST':
        password = request.form.get('pwd')
        user = User.get_by_email(email)
        if email and password:
            if user and User.check_password(user.password, password):
                if request.form.get('remember'):
                    login_user(user, remember=True)
                else:
                    login_user(user)
                return redirect(url_for('main'))
            else:
                flash('Login or password is not correct')
        else:
            flash('Please fill login and password fields')
    if not email:
        email = ''
    return render_template('login.html', categories=categories, email=email)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth'))

@app.route('/add_advert', methods=['GET', 'POST'])
@login_required
def add_advert():
    context = {
        'title': request.form.get('title'),
        'description': request.form.get('desc'),
        'category': request.form.get('cat'),
        'price': request.form.get('price'),
        'image_url': request.form.get('img_url'),
        'user_id': current_user.id
    }

    if request.method == 'POST':

        if context['title'] and context['description'] and context['category'] and context['price']:
            adv = Advert(**context)
            adv.save()

            return redirect(url_for('advert', page_id=adv.id))

        flash('Title, description, category and price are required fields! Please, enter this fields.')

    for key in context:
        if context[key] is None:
            context[key] = ''
    context['categories'] = categories

    return render_template('add_advert.html', **context)


@app.route('/advert/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_advert(page_id):
    adv = Advert.get_by_id(page_id, 'adverts')
    if current_user.id == adv.user_id:

        context = {
            'title': adv.title,
            'description': adv.description,
            'category': adv.category,
            'price': adv.price,
            'image_url': adv.image_url,
            'user_id': adv.user_id,
            'id': adv.id,
            'categories': categories
        }

        if request.method == 'POST':
            new_values = [
                request.form.get('title'),
                request.form.get('desc'),
                request.form.get('cat'),
                request.form.get('price'),
                request.form.get('img_url'),
                current_user.id
            ]

            if new_values[0] and new_values[1] and new_values[2] and new_values[3]:
                adv.update(
                    'adverts',
                    'title description category price image_url user_id',
                    new_values
                )

                return redirect(url_for('advert', page_id=page_id))

            flash('Title, description, category and price are required fields! Please, enter this fields.')

        for key in context:
            if context[key] is None:
                context[key] = ''

        return render_template('edit_advert.html', **context)
    return redirect(url_for('advert', page_id=page_id))


@app.route('/advert/<int:page_id>/delete')
@login_required
def delete_advert(page_id):
    adv = Advert.get_by_id(page_id, 'adverts')
    if current_user.id == adv.user_id or current_user.admin_status:
        adv.delete()
        return redirect(url_for('main'))
    return redirect(url_for('advert', id=page_id))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', categories=categories)


@app.route('/profile/delete')
@login_required
def delete_profile():
    if not current_user.admin_status:
        user = current_user
        user.delete()
        return redirect(url_for('auth'))
    return redirect(url_for('profile'))


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    context = {
        'email': current_user.email,
        'name': current_user.name,
        'image_url': current_user.image_url,
        'categories': categories
    }

    if request.method == 'POST':
        new_data_names = 'email name'
        new_data = [request.form.get('email'), request.form.get('name')]
        image_url = request.form.get('image_url')
        password = request.form.get('password')
        password_retype = request.form.get('password2')

        if image_url:
            new_data_names += ' image_url'
            new_data.append(image_url)

        if new_data[0]:
            if password:
                if password_retype:
                    if password == password_retype:
                        new_data_names += ' password'
                        new_data.append(bcrypt.hashpw(password.encode(), bcrypt.gensalt()).hex())
                    else:
                        flash("Passwords don't match!")
                        return render_template('edit_profile.html', **context)
                else:
                    flash("Enter password retype!")
                    return render_template('edit_profile.html', **context)

            current_user.update('users', new_data_names, new_data)

            return redirect(url_for('profile'))

        flash('Email a required field! Please, enter email.')

    return render_template('edit_profile.html', **context)


@app.route('/cart')
@login_required
def cart():
    in_cart = Cart.get_by_user_id(current_user.id, 'cart')
    advs_in_cart = []
    for adv_in_cart in in_cart:
        adv = Advert.get_by_id(adv_in_cart.advert_id, 'adverts')
        advs_in_cart.append(adv)

    summa = sum([adv.price for adv in advs_in_cart])

    context = {
        'adverts': advs_in_cart,
        'summa': summa,
        'categories': categories
    }

    return render_template('cart.html', **context)


@app.route('/advert/<int:page_id>/add_to_cart')
@login_required
def add_to_cart(page_id):
    if not Cart.get_by_user_advert('cart', current_user.id, page_id):
        adv_in_cart = Cart(current_user.id, page_id)
        adv_in_cart.save()
    return redirect(url_for('advert', page_id=page_id))


@app.route('/cart/delete/<int:adv_id>/<int:from_advert>')
@login_required
def delete_from_cart(adv_id, from_advert):
    adv_in_cart = Cart.get_by_user_advert('cart', current_user.id, adv_id)
    adv_in_cart.delete('cart')
    if from_advert:
        return redirect(url_for('advert', page_id=adv_id))
    return redirect(url_for('cart'))


@app.route('/favorites')
@login_required
def favorites():
    search = request.args.get('search')
    if not search:
        search = ''
    in_favorites = Favorite.get_by_user_id(current_user.id, 'favorites')
    advs_in_favorites = []
    for adv_in_fav in in_favorites:
        advs = Advert.get_all_by_filters(id=adv_in_fav.advert_id, search=search)
        advs_in_favorites += advs

    context = {
        'adverts': advs_in_favorites,
        'categories': categories
    }

    return render_template('favorites.html', **context)


@app.route('/advert/<int:page_id>/add_to_favorites')
@login_required
def add_to_favorites(page_id):
    if not Favorite.get_by_user_advert('favorites', current_user.id, page_id):
        adv_to_favorites = Favorite(current_user.id, page_id)
        adv_to_favorites.save()
    return redirect(url_for('advert', page_id=page_id))


@app.route('/favorites/delete/<int:adv_id>/<int:from_advert>')
@login_required
def delete_from_favorites(adv_id, from_advert):
    adv_in_fav = Favorite.get_by_user_advert('favorites', current_user.id, adv_id)
    adv_in_fav.delete('favorites')
    if from_advert:
        return redirect(url_for('advert', page_id=adv_id))
    return redirect(url_for('favorites'))


@app.route('/make_order')
@login_required
def make_order():
    advs_in_cart = Cart.get_by_user_id(current_user.id, 'cart')

    advs = [Advert.get_by_id(adv_in_cart.advert_id, 'adverts') for adv_in_cart in advs_in_cart]
    summa = sum([adv.price for adv in advs])
    order = Order(summa, current_user.id)
    order.save()

    for adv in advs:
        purch = Purchase(adv.id, order.id)
        purch.save()
        adv.hidden()

    for adv_in_cart in advs_in_cart:
        adv_in_cart.delete('cart')

    return redirect(url_for('orders_page'))


@app.route('/orders')
@login_required
def orders_page():
    orders = Order.get_by_user_id(current_user.id, 'orders')

    context = {
        'orders': orders[::-1],
        'categories': categories
    }

    return render_template('orders.html', **context)


@app.route('/orders/<int:page_id>')
@login_required
def order_page(page_id):
    order = Order.get_by_id(page_id, 'orders')
    purchases = Purchase.get_by_order_id(order.id)
    advs = [Advert.get_by_id(purch.advert_id, 'adverts') for purch in purchases]

    context = {
        'order': order,
        'adverts': advs,
        'categories': categories
    }

    return render_template('order.html', **context)


if __name__ == '__main__':
    app.run()
