from decimal import Decimal

from django.test import TestCase

from apps.core.models import Branch, User
from apps.pos.models import Category, Product, Sale, SaleItem
from .services import sales_by_product


class SalesByProductTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.create(name='Central', code='CENT', address='Dir')
        cls.user = User.objects.create_user(username='cashier', branch=cls.branch)
        cls.category = Category.objects.create(name='General')
        cls.first_product = Product.objects.create(
            sku='SKU1', name='Item', category=cls.category,
            price=Decimal('10.00'), branch=cls.branch,
        )
        cls.second_product = Product.objects.create(
            sku='SKU2', name='Item', category=cls.category,
            price=Decimal('20.00'), branch=cls.branch,
        )

    def create_sale(self, branch, items):
        sale = Sale.objects.create(
            branch=branch, cashier=self.user, payment_method='cash',
            total=sum(product.price * quantity for product, quantity in items),
        )
        for product, quantity in items:
            SaleItem.objects.create(
                sale=sale, product=product, quantity=quantity,
                unit_price=product.price,
            )

    def test_same_named_products_are_separate_and_ordered_by_total_quantity(self):
        self.create_sale(self.branch, [
            (self.first_product, 2),
            (self.second_product, 5),
        ])
        self.create_sale(self.branch, [(self.first_product, 1)])

        self.assertEqual(list(sales_by_product(self.branch)), [
            {
                'product__id': self.second_product.id,
                'product__sku': 'SKU2',
                'product__name': 'Item',
                'total': 5,
            },
            {
                'product__id': self.first_product.id,
                'product__sku': 'SKU1',
                'product__name': 'Item',
                'total': 3,
            },
        ])

    def test_sales_from_other_branches_are_excluded(self):
        other_branch = Branch.objects.create(name='North', code='NORTH', address='Dir')
        other_product = Product.objects.create(
            sku='SKU3', name='Item', category=self.category,
            price=Decimal('30.00'), branch=other_branch,
        )
        self.create_sale(self.branch, [(self.first_product, 2)])
        self.create_sale(other_branch, [(other_product, 100)])

        self.assertEqual(list(sales_by_product(self.branch)), [
            {
                'product__id': self.first_product.id,
                'product__sku': 'SKU1',
                'product__name': 'Item',
                'total': 2,
            },
        ])
