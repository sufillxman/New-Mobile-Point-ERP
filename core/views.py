from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Customer, Product, Invoice, Expense
from .forms import CustomerForm, InvoiceForm, ProductForm, ExpenseForm
from decimal import Decimal
from datetime import date, timedelta

@login_required
def dashboard(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    monthly_invoices = Invoice.objects.filter(sale_date__month=month, sale_date__year=year)
    monthly_expenses = Expense.objects.filter(date__month=month, date__year=year)
    
    total_sales = monthly_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_received = monthly_invoices.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_pending = monthly_invoices.aggregate(Sum('balance_amount'))['balance_amount__sum'] or 0
    total_expense = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    sales_profit = sum(inv.get_profit() for inv in monthly_invoices)
    net_profit = float(sales_profit) - float(total_expense)

    overdue_payments = Invoice.objects.filter(due_date__lt=today, balance_amount__gt=0).order_by('due_date')
    payments_due_today = Invoice.objects.filter(due_date=today, balance_amount__gt=0)

    next_week = today + timedelta(days=1)
    upcoming_payments = Invoice.objects.filter(
        due_date__gt=today, 
        due_date__lte=next_week, 
        balance_amount__gt=0
    ).order_by('due_date')

    available_products = Product.objects.filter(is_available=True)
    out_of_stock_count = Product.objects.filter(is_available=False).count()
    pending_invoices = Invoice.objects.filter(balance_amount__gt=0).order_by('due_date')

    context = {
        'total_sales': total_sales,
        'total_received': total_received,
        'total_pending': total_pending,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'available_products': available_products,
        'out_of_stock_count': out_of_stock_count,
        'pending_invoices': pending_invoices,
        'overdue_payments': overdue_payments,
        'payments_due_today': payments_due_today,
        'upcoming_payments': upcoming_payments,
        'selected_month': month,
        'selected_year': year,
        'months_range': range(1, 13),
        'years_range': range(today.year - 2, today.year + 1),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f"Customer {customer.name} added!")
            next_page = request.GET.get('next')
            if next_page == 'billing':
                return redirect('create_invoice')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'core/add_customer.html', {'form': form})

@login_required
def customer_list(request):
    query = request.GET.get('q', '')
    if query:
        customers = Customer.objects.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    else:
        customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'core/customer_list.html', {'customers': customers, 'query': query})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    invoices = Invoice.objects.filter(customer=customer).order_by('-sale_date')
    customer_pending = invoices.aggregate(Sum('balance_amount'))['balance_amount__sum'] or 0
    return render(request, 'core/customer_detail.html', {
        'customer': customer,
        'invoices': invoices,
        'customer_pending': customer_pending,
    })

@login_required
def stock_list(request):
    products = Product.objects.all().order_by('-is_available', 'brand')
    return render(request, 'core/stock_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock Added!")
            return redirect('stock_list')
    else:
        form = ProductForm()
    return render(request, 'core/add_product.html', {'form': form})

@login_required
def mark_stock_sold(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_available = not product.is_available
    product.save()
    status = "AVAILABLE" if product.is_available else "SOLD OUT"
    messages.info(request, f"Stock marked as {status}")
    return redirect('stock_list')

@login_required
def create_invoice(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            product = invoice.product
            product.is_available = False
            product.save()
            invoice.save()
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    return render(request, 'core/create_invoice.html', {'form': form})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'core/invoice_detail.html', {'invoice': invoice})

@login_required
def add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == "POST":
        received_str = request.POST.get('amount_received')
        
        if received_str:
            # String ko Number (Decimal) mein badlo
            received_amount = Decimal(received_str) 
            
            # 1. Purane jama mein naya amount jodo
            invoice.amount_paid += received_amount
            
            # 2. Safety check: Total se zyada paise nahi le sakte
            if invoice.amount_paid > invoice.total_amount:
                invoice.amount_paid = invoice.total_amount
            
            # 3. Save karte hi models.py wala logic balance nikaal dega
            invoice.save()
            
            messages.success(request, f"₹{received_amount} jama ho gaye!")
            
            # 4. Agar poora paisa aa gaya toh Dashboard, warna wapas Detail page
            if invoice.balance_amount == 0:
                return redirect('dashboard')
            else:
                return redirect('customer_detail', pk=invoice.customer.pk)
                
    return render(request, 'core/add_payment.html', {'invoice': invoice})

@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense Added!")
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'core/add_expense.html', {'form': form})