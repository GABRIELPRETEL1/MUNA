from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models, transaction
from apps.core.models import Branch


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Product(models.Model):
    sku = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


class Customer(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)


class Sale(models.Model):
    PAYMENT_METHODS = [('cash', 'Efectivo'), ('card', 'Tarjeta'), ('transfer', 'Transferencia')]
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    cashier = models.ForeignKey('core.User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)


class CashRegisterClosure(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    manager = models.ForeignKey('core.User', on_delete=models.PROTECT)
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2)
    counted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    variance = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def close_register(cls, branch, manager, expected_amount, counted_amount):
        variance = counted_amount - expected_amount
        return cls.objects.create(branch=branch, manager=manager, expected_amount=expected_amount, counted_amount=counted_amount, variance=variance)


class SaleService:
    @staticmethod
    @transaction.atomic
    def process_sale(branch, cashier, items, payment_method, customer=None):
        total = Decimal('0.00')
        sale = Sale.objects.create(branch=branch, cashier=cashier, customer=customer, total=0, payment_method=payment_method)
        for item in items:
            product = Product.objects.select_for_update().get(pk=item['product_id'], branch=branch)
            qty = int(item['quantity'])
            if qty <= 0:
                raise ValueError('Cantidad inválida')
            if product.stock < qty:
                raise ValueError(f'Stock insuficiente para {product.name}')
            product.stock -= qty
            product.save(update_fields=['stock'])
            line_total = product.price * qty
            total += line_total
            SaleItem.objects.create(sale=sale, product=product, quantity=qty, unit_price=product.price)
        sale.total = total
        sale.save(update_fields=['total'])
        return sale
