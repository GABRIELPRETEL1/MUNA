from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from apps.core.models import Branch, User
from .models import Category, Product, Sale, SaleItem, SaleService


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
        self.assertEqual(Sale.objects.count(), 1)
        line = SaleItem.objects.get(sale=sale)
        self.assertEqual(line.product, self.product)
        self.assertEqual(line.quantity, 2)
        self.assertEqual(line.unit_price, Decimal('10.00'))

    def test_process_sale_rejects_inactive_product(self):
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])

        with self.assertRaises(Product.DoesNotExist):
            SaleService.process_sale(
                self.branch, self.user,
                [{'product_id': self.product.id, 'quantity': 2}], 'cash',
            )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(SaleItem.objects.count(), 0)

    def test_process_sale_rolls_back_when_later_product_is_inactive(self):
        inactive_product = Product.objects.create(
            sku='SKU2', name='Inactive item', category=self.category,
            price=Decimal('10.00'), stock=5, branch=self.branch, is_active=False,
        )

        with self.assertRaises(Product.DoesNotExist):
            SaleService.process_sale(self.branch, self.user, [
                {'product_id': self.product.id, 'quantity': 2},
                {'product_id': inactive_product.id, 'quantity': 1},
            ], 'cash')

        self.product.refresh_from_db()
        inactive_product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(inactive_product.stock, 5)
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(SaleItem.objects.count(), 0)


class CheckoutTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name='Central', code='CENT', address='Dir')
        self.user = User.objects.create_user(username='cashier', branch=self.branch)
        self.category = Category.objects.create(name='General')
        self.product = Product.objects.create(
            sku='SKU1', name='Item', category=self.category,
            price=Decimal('10.00'), stock=5, branch=self.branch,
        )
        self.client.force_login(self.user)

    def test_checkout_rejects_inactive_product_post(self):
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])

        response = self.client.post(reverse('checkout'), {
            'product_id': self.product.id, 'quantity': 2, 'payment_method': 'cash',
        })

        self.assertEqual(response.status_code, 404)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(SaleItem.objects.count(), 0)

    def test_checkout_sells_active_product(self):
        response = self.client.post(reverse('checkout'), {
            'product_id': self.product.id, 'quantity': 2, 'payment_method': 'cash',
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        sale = Sale.objects.get()
        self.assertEqual(sale.branch, self.branch)
        self.assertEqual(sale.cashier, self.user)
        self.assertEqual(sale.total, Decimal('20.00'))
        self.assertEqual(sale.payment_method, 'cash')
        line = SaleItem.objects.get(sale=sale)
        self.assertEqual(line.product, self.product)
        self.assertEqual(line.quantity, 2)
        self.assertEqual(line.unit_price, Decimal('10.00'))
