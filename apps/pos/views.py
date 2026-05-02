from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from .forms import SaleCheckoutForm
from .models import Product, Sale, SaleService

@login_required
def dashboard(request):
    low_stock = Product.objects.filter(stock__lte=5, is_active=True)[:20]
    daily_total = Sale.objects.filter(branch=request.user.branch).aggregate(total=Sum('total'))['total'] or 0
    return render(request, 'pos/dashboard.html', {'low_stock': low_stock, 'daily_total': daily_total})

@login_required
def checkout(request):
    if request.method == 'POST':
        form = SaleCheckoutForm(request.POST)
        if form.is_valid():
            product = get_object_or_404(Product, pk=request.POST.get('product_id'), branch=request.user.branch)
            qty = int(request.POST.get('quantity', 1))
            SaleService.process_sale(request.user.branch, request.user, [{'product_id': product.id, 'quantity': qty}], form.cleaned_data['payment_method'])
            return redirect('dashboard')
    else:
        form = SaleCheckoutForm()
    return render(request, 'pos/checkout.html', {'form': form, 'products': Product.objects.filter(branch=request.user.branch, is_active=True)})
