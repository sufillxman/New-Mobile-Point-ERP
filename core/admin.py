from django.contrib import admin
from .models import Customer, Product, Invoice, Expense
from django.utils.html import format_html

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="45" style="border-radius:50%;" />', obj.photo.url)
        return "No Photo"
    
    display_photo.short_description = 'DP'
    list_display = ('display_photo', 'name', 'phone', 'created_at')
    search_fields = ('name', 'phone')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def profit_margin(self, obj):
        margin = obj.selling_price - obj.purchase_price
        return f"₹{margin}"
    
    profit_margin.short_description = 'Margin'
    list_display = ('brand', 'model_name', 'imei', 'selling_price', 'profit_margin', 'is_available')
    list_filter = ('brand', 'is_available')
    search_fields = ('model_name', 'imei')
    list_editable = ('is_available',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    def calculate_profit(self, obj):
        profit = obj.get_profit()
        color = "green" if profit > 0 else "red"
        return format_html('<b style="color: {};">₹{}</b>', color, profit)
    
    calculate_profit.short_description = 'Profit Made'

    def balance_status(self, obj):
        if obj.balance_amount > 0:
            return format_html('<span style="color: orange; font-weight: bold;">₹{} (DUE)</span>', obj.balance_amount)
        return format_html('<span style="color: green; font-weight: bold;">PAID</span>')
    
    balance_status.short_description = 'Balance Status'

    list_display = ('id', 'customer', 'product', 'total_amount', 'amount_paid', 'balance_status', 'calculate_profit', 'sale_date')
    list_filter = ('payment_mode', 'sale_date')
    search_fields = ('customer__name', 'product__model_name', 'transaction_id')
    readonly_fields = ('balance_amount', 'sale_date')

    fieldsets = (
        ('Customer & Product', {
            'fields': ('customer', 'product')
        }),
        ('Payment Info', {
            'fields': ('total_amount', 'amount_paid', 'balance_amount', 'payment_mode', 'transaction_id', 'due_date')
        }),
    )

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'expense_type', 'date')
    list_filter = ('expense_type', 'date')
    search_fields = ('title',)