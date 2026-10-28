from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Table, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()
order_product_association = Table(
    'order_product_association', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    total_price = Column(Numeric(10, 2), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="orders")
    products = relationship("Product", secondary=order_product_association, back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, total_price={self.total_price})>"

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    orders = relationship("Order", secondary=order_product_association, back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


print("Создание текстовых данных")

p1 = Product(name="Ноутбук", price=1000.00)
p2 = Product(name="Мышь", price=50.00)
p3 = Product(name="Клавиатура", price=150.00)

user = User(name="Ромчик Процак")

order1 = Order(total_price=1050.00, user=user)
order2 = Order(total_price=1150.00, user=user)

order1.products.append(p1) 
order1.products.append(p2) 

order2.products.append(p1) 
order2.products.append(p3) 

session.add_all([user, order1, order2])
session.commit()

print("Данные успешно добавлены в БД")
print("Создан 1 пользователь, 2 заказа, 3 товара")
print("Товар 'Ноутбук' входит в оба заказа.\n")


print("Демонстрация чтения данных\n")
print("Связь один-ко-многим (User <-> Order)")

db_user = session.query(User).filter_by(name="Ромчик Процак").first()
print(f"От пользователя к заказам (Пользователь: {db_user.name}):")
for order in db_user.orders:
    print(f"Заказ №{order.id}, сумма: {order.total_price} руб.")

db_order = session.query(Order).first()
print(f"От заказа к пользователю (Заказ №{db_order.id}, сумма: {db_order.total_price} руб.):")
print(f"Владелец заказа: {db_order.user.name}\n")


print("Связь многие-ко-многим (Order <-> Product)")

print(f"От заказа к товарам (Заказ №{db_order.id}):")
for prod in db_order.products:
    print(f"Товар: {prod.name}, цена: {prod.price} руб.")

db_product = session.query(Product).filter_by(name="Ноутбук").first()
print(f"От товара к заказам (Товар: {db_product.name}):")
for ord in db_product.orders:
    print(f"Заказ №{ord.id} (Владелец: {ord.user.name}, Сумма: {ord.total_price} руб.)")

session.close()