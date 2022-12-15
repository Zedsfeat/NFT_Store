import psycopg2

con = psycopg2.connect(
    dbname='NFTPictureStore',
    user='postgres',
    password='importPower1q2w3e4r'
)

cur = con.cursor()

if __name__ == '__main__':
    cur.execute(
        '''create table users
           (
               email varchar(255) NOT NULL UNIQUE,
               password varchar NOT NULL,
               name varchar(255),
               image_url text,
               admin_status bool default false,
               id serial NOT NULL UNIQUE,
               registration_date date default current_date,
               PRIMARY KEY (id)
           );
           
           create table adverts
           (
               title varchar(255) NOT NULL,
               description text NOT NULL,
               category varchar NOT NULL,
               price double precision NOT NULL,
               image_url text,
               user_id integer,
               id serial NOT NULL UNIQUE,
               is_active boolean default true,
               PRIMARY KEY (id),
               CONSTRAINT user_fk
                   FOREIGN KEY (user_id)
                       REFERENCES users (id)
                       ON DELETE SET NULL
           );
           
           create table cart
           (
               user_id integer NOT NULL,
               advert_id integer NOT NULL,
               CONSTRAINT user_fk
                   FOREIGN KEY (user_id)
                       REFERENCES users (id)
                       ON DELETE CASCADE,
               CONSTRAINT advert_fk
                   FOREIGN KEY (advert_id)
                       REFERENCES adverts (id)
           );
           
           create table orders
           (
                total double precision NOT NULL,
                user_id integer NOT NULL,
                id serial NOT NULL UNIQUE,
                created_at date default current_date,
                PRIMARY KEY (id),
                CONSTRAINT user_fk
                    FOREIGN KEY (user_id)
                        REFERENCES users (id)
                        ON DELETE CASCADE
           );
           
           create table purchases
           (
               advert_id integer NOT NULL,
               order_id integer NOT NULL,
               CONSTRAINT advert_fk
                   FOREIGN KEY (advert_id)
                       REFERENCES adverts (id),
               CONSTRAINT orders_fk
                   FOREIGN KEY (order_id)
                       REFERENCES orders (id)
                       ON DELETE CASCADE
           );
           
           create table favorites
           (
               user_id integer NOT NULL,
               advert_id integer NOT NULL,
               CONSTRAINT user_fk
                   FOREIGN KEY (user_id)
                       REFERENCES users (id)
                       ON DELETE CASCADE,
               CONSTRAINT advert_fk
                   FOREIGN KEY (advert_id)
                       REFERENCES adverts (id)
                       ON DELETE CASCADE
           );
           '''
    )
    con.commit() # Сохранение изменений
