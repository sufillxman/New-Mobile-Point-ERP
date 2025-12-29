from django import forms
from .models import Customer, Product, Invoice, Expense

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 
                'placeholder': 'Customer Full Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 
                'placeholder': '10 Digit Mobile No'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 
                'rows': 3, 
                'placeholder': 'Full Address'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg bg-gray-50'
            }),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'product', 'total_amount', 'amount_paid', 'payment_mode', 'transaction_id', 'due_date']
        widgets = {
            'customer': forms.Select(attrs={'class': 'w-full p-3 border border-gray-300 rounded-lg'}),
            'product': forms.Select(attrs={'class': 'w-full p-3 border border-gray-300 rounded-lg'}),
            'total_amount': forms.NumberInput(attrs={'class': 'w-full p-3 border border-gray-300 rounded-lg', 'placeholder': 'Final Deal Price'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'w-full p-3 border border-gray-300 rounded-lg', 'placeholder': 'Paid Amount'}),
            'payment_mode': forms.Select(attrs={'class': 'w-full p-3 border border-gray-300 rounded-lg'}),
            'transaction_id': forms.TextInput(attrs={'class': 'w-full p-3 border border-gray-300 rounded-lg', 'placeholder': 'UPI ID / Finance File No'}),
            'due_date': forms.DateInput(attrs={'class': 'w-full p-3 border border-gray-300 rounded-lg', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_available=True)
        self.fields['customer'].label_from_instance = lambda obj: f"{obj.name} ({obj.phone})"
        self.fields['product'].label_from_instance = lambda obj: f"{obj.model_name} - ₹{obj.selling_price}"

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['brand', 'model_name', 'imei', 'purchase_price', 'selling_price']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'Ex: Samsung, Apple'}),
            'model_name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'Ex: Galaxy S23'}),
            'imei': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'Scan IMEI'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'Kharid Bhav'}),
            'selling_price': forms.NumberInput(attrs={'class': 'w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'Bechne Ka Bhav'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'expense_type', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-3 border rounded-lg'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. November Rent', 'class': 'w-full p-3 border rounded-lg'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Amount in ₹', 'class': 'w-full p-3 border rounded-lg'}),
            'expense_type': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }