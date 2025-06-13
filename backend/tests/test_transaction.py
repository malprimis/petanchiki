from datetime import datetime
from decimal import Decimal

from app.db.base import UserRole, TransactionType
from app.models.category import Category
from app.models.group import Group
from app.models.transaction import Transaction
from app.models.user import User


def test_transaction_fields_and_relationships(db_session):
    # Подготовка пользователя и группы
    user = User(
        email="txnuser@example.com",
        name="TXN",
        password_hash="h",
        role=UserRole.user
    )
    group = Group(name="TXN Group", owner=user)
    db_session.add_all([user, group])
    db_session.flush()

    # Создаём категорию для транзакции
    category = Category(
        group=group,
        name="Test Category",
        icon=None
    )
    db_session.add(category)
    db_session.flush()

    # Создаём транзакцию и явно задаём дату, чтобы обойти server_default в SQLite
    tx_date = datetime.now()
    tx = Transaction(
        group=group,
        user=user,
        category=category,
        amount=Decimal('99.99'),
        type=TransactionType.expense,
        date=tx_date
    )
    db_session.add(tx)
    db_session.flush()

    # Проверяем, что FK выставлены и relationship доступны
    assert tx.group is group
    assert tx.user is user
    assert tx.category is category

    # Проверяем значения полей
    assert tx.amount == Decimal('99.99')
    assert tx.type == TransactionType.expense
    assert tx.date == tx_date