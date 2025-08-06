# customer/admin.py
from django.contrib import admin
from .models import Customer, Cart, CartItem, CustomerOrder, CustomerOrderItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'session_key', 'total_items', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer__name', 'session_key')
    readonly_fields = ('created_at', 'updated_at', 'total_items', 'total_amount')
    inlines = [CartItemInline]

class CustomerOrderItemInline(admin.TabularInline):
    model = CustomerOrderItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'status', 'order_type', 'total_amount', 'created_at')
    list_filter = ('status', 'order_type', 'payment_status', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [CustomerOrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'payment_status', 'order_type', 'total_amount')
        }),
        ('Customer Information', {
            'fields': ('customer', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Order Details', {
            'fields': ('table_number', 'delivery_address', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
