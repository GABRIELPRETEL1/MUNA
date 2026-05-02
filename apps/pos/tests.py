from decimal import Decimal
from django.test import TestCase
from apps.core.models import Branch, User
from .models import Category, Product, SaleService


class SaleServiceTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name='Central', code='CENT', address='Dir')
        self.user = User.objects.create_user(username='cashier', password='123', branch=self.branch)
        self.category = Category.objects.create(name='General')
        self.product = Product.objects.create(sku='SKU1', name='Item', category=self.category, price=Decimal('10.00'), stock=5, branch=self.branch)

    def test_process_sale_updates_stock_and_total(self):
        sale = SaleService.process_sale(self.branch, self.user, [{'product_id': self.product.id, 'quantity': 2}], 'cash')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(sale.total, Decimal('20.00'))
