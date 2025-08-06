# customer/urls.py
from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    # Customer interface
    path('', views.MenuView.as_view(), name='menu'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order-confirmation/<str:order_number>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('track-order/', views.OrderTrackingView.as_view(), name='track_order'),
    
    # Admin interface for customer orders
    path('admin/orders/', views.CustomerOrderListView.as_view(), name='admin_order_list'),
    path('admin/orders/<int:order_id>/update-status/', views.update_customer_order_status, name='update_order_status'),
    
    # API endpoints
    path('api/add-to-cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('api/update-cart-item/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('api/remove-from-cart/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('api/cart-info/', views.get_cart_info, name='cart_info'),
]