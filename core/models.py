from django.db import models
from django.utils import timezone
from datetime import date

class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="Customer Name")
    phone = models.CharField(max_length=10, unique=True, verbose_name="Mobile Number")
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='customers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    brand = models.CharField(max_length=50, verbose_name="Brand")
    model_name = models.CharField(max_length=100, verbose_name="Model Name")
    imei = models.CharField(max_length=15, unique=True, verbose_name="IMEI Number")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2) 
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)  
    is_available = models.BooleanField(default=True, verbose_name="In Stock") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model_name} - {self.imei}"

class Invoice(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('BAJAJ', 'Bajaj Finance'),
        ('ONLINE', 'UPI / Online'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='invoice_details')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Final Deal Price")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Paid Now")
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    sale_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.balance_amount = self.total_amount - self.amount_paid
        super().save(*args, **kwargs)

    def get_profit(self):
        if self.product:
            return self.total_amount - self.product.purchase_price
        return 0

    def status(self):
        return "DUE" if self.balance_amount > 0 else "PAID"

    def __str__(self):
        return f"Bill #{self.id} - {self.customer.name}"

class Expense(models.Model):
    EXPENSE_TYPES = [   
        ('Rent', 'Rent'),
        ('Electricity', 'Electricity'),
        ('Tea/Food', 'Tea & Snacks'),
        ('Others', 'Others'),
    ]
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES)
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"