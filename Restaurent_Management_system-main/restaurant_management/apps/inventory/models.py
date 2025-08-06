# apps/inventory/models.py
from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    CATEGORY_TYPES = [
        ('appetizer', 'Appetizers'),
        ('main_course', 'Main Course'),
        ('soup', 'Soups'),
        ('dessert', 'Desserts'),
        ('beverage', 'Beverages'),
        ('salad', 'Salads'),
        ('side', 'Sides'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='main_course')
    description = models.TextField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, 
        related_name='menu_items', 
        on_delete=models.CASCADE
    )
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        upload_to='menu_items/', 
        blank=True, 
        null=True
    )
    is_available = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold