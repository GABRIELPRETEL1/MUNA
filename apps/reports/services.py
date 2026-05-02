from django.db.models import Sum
from django.db.models.functions import TruncMonth
from apps.pos.models import Sale, SaleItem


def daily_sales(branch, date):
    return Sale.objects.filter(branch=branch, created_at__date=date).aggregate(total=Sum('total'))


def monthly_sales(branch):
    return Sale.objects.filter(branch=branch).annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total')).order_by('month')


def sales_by_product(branch):
    return SaleItem.objects.filter(sale__branch=branch).values('product__name').annotate(total=Sum('quantity')).order_by('-total')
