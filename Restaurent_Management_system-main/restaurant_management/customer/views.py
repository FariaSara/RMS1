# customer/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib import messages
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db import models
import json
import random
import string

from apps.inventory.models import Category, MenuItem
from .models import Customer, Cart, CartItem, CustomerOrder, CustomerOrderItem


# Customer Views (existing)
class MenuView(View):
    def get(self, request):
        categories = Category.objects.filter(is_active=True).prefetch_related('menu_items')
        cart = self.get_or_create_cart(request)
        
        # Organize menu items by category
        menu_data = {}
        for category in categories:
            menu_items = category.menu_items.filter(is_available=True)
            if menu_items.exists():
                menu_data[category] = menu_items
        
        context = {
            'menu_data': menu_data,
            'cart': cart,
            'cart_total': cart.total_amount if cart else 0,
            'cart_items_count': cart.total_items if cart else 0,
        }
        return render(request, 'customer/menu.html', context)
    
    def get_or_create_cart(self, request):
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            defaults={'session_key': request.session.session_key}
        )
        return cart


class AddToCartView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            menu_item_id = data.get('menu_item_id')
            quantity = int(data.get('quantity', 1))
            
            menu_item = get_object_or_404(MenuItem, id=menu_item_id, is_available=True)
            
            if not request.session.session_key:
                request.session.create()
            
            cart, created = Cart.objects.get_or_create(
                session_key=request.session.session_key,
                defaults={'session_key': request.session.session_key}
            )
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                menu_item=menu_item,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{menu_item.name} added to cart',
                'cart_total': float(cart.total_amount),
                'cart_items_count': cart.total_items,
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class CartView(View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.all() if cart else [],
        }
        return render(request, 'customer/cart.html', context)
    
    def get_cart(self, request):
        if not request.session.session_key:
            return None
        try:
            return Cart.objects.get(session_key=request.session.session_key)
        except Cart.DoesNotExist:
            return None


class UpdateCartItemView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            cart_item_id = data.get('cart_item_id')
            quantity = int(data.get('quantity', 1))
            
            cart_item = get_object_or_404(CartItem, id=cart_item_id)
            
            if quantity <= 0:
                cart_item.delete()
                message = 'Item removed from cart'
            else:
                cart_item.quantity = quantity
                cart_item.save()
                message = 'Cart updated'
            
            cart = cart_item.cart
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_total': float(cart.total_amount),
                'cart_items_count': cart.total_items,
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class RemoveFromCartView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            cart_item_id = data.get('cart_item_id')
            
            cart_item = get_object_or_404(CartItem, id=cart_item_id)
            cart = cart_item.cart
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart',
                'cart_total': float(cart.total_amount),
                'cart_items_count': cart.total_items,
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class CheckoutView(View):
    def get(self, request):
        cart = self.get_cart(request)
        if not cart or not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('customer:menu')
        
        context = {
            'cart': cart,
            'cart_items': cart.items.all(),
        }
        return render(request, 'customer/checkout.html', context)
    
    def post(self, request):
        cart = self.get_cart(request)
        if not cart or not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('customer:menu')
        
        # Get form data
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        order_type = request.POST.get('order_type', 'dine_in')
        table_number = request.POST.get('table_number')
        notes = request.POST.get('notes', '')
        
        if not all([customer_name, customer_email, customer_phone]):
            messages.error(request, 'Please fill in all required fields.')
            return self.get(request)
        
        try:
            with transaction.atomic():
                # Generate order number
                order_number = self.generate_order_number()
                
                # Create customer order
                customer_order = CustomerOrder.objects.create(
                    order_number=order_number,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    total_amount=cart.total_amount,
                    order_type=order_type,
                    table_number=int(table_number) if table_number else None,
                    notes=notes,
                    status='confirmed'
                )
                
                # Create order items
                for cart_item in cart.items.all():
                    CustomerOrderItem.objects.create(
                        order=customer_order,
                        menu_item=cart_item.menu_item,
                        quantity=cart_item.quantity,
                        price_at_time=cart_item.menu_item.price
                    )
                
                # Clear cart
                cart.items.all().delete()
                
                messages.success(request, f'Order #{order_number} placed successfully!')
                return redirect('customer:order_confirmation', order_number=order_number)
                
        except Exception as e:
            messages.error(request, f'Error placing order: {str(e)}')
            return self.get(request)
    
    def get_cart(self, request):
        if not request.session.session_key:
            return None
        try:
            return Cart.objects.get(session_key=request.session.session_key)
        except Cart.DoesNotExist:
            return None
    
    def generate_order_number(self):
        while True:
            order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not CustomerOrder.objects.filter(order_number=order_number).exists():
                return order_number


class OrderConfirmationView(View):
    def get(self, request, order_number):
        order = get_object_or_404(CustomerOrder, order_number=order_number)
        context = {
            'order': order,
            'order_items': order.items.all(),
        }
        return render(request, 'customer/order_confirmation.html', context)


class OrderTrackingView(View):
    def get(self, request):
        order_number = request.GET.get('order_number')
        order = None
        
        if order_number:
            try:
                order = CustomerOrder.objects.get(order_number=order_number.upper())
            except CustomerOrder.DoesNotExist:
                messages.error(request, 'Order not found.')
        
        context = {
            'order': order,
            'order_items': order.items.all() if order else [],
        }
        return render(request, 'customer/order_tracking.html', context)


# Admin Views for Customer Order Management
class CustomerOrderListView(LoginRequiredMixin, ListView):
    model = CustomerOrder
    template_name = 'customer/admin/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CustomerOrder.objects.all().order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by order type
        order_type = self.request.GET.get('order_type')
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        
        # Search by order number or customer name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(order_number__icontains=search) |
                models.Q(customer_name__icontains=search) |
                models.Q(customer_email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = CustomerOrder.ORDER_STATUS
        context['order_type_choices'] = [('dine_in', 'Dine In'), ('takeaway', 'Takeaway')]
        context['current_status'] = self.request.GET.get('status', '')
        context['current_order_type'] = self.request.GET.get('order_type', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


@login_required
def update_customer_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(CustomerOrder, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in [choice[0] for choice in CustomerOrder.ORDER_STATUS]:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.order_number} status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('customer:admin_order_list')


@require_http_methods(["GET"])
def get_cart_info(request):
    """API endpoint to get current cart information"""
    if not request.session.session_key:
        return JsonResponse({'cart_items_count': 0, 'cart_total': 0})
    
    try:
        cart = Cart.objects.get(session_key=request.session.session_key)
        return JsonResponse({
            'cart_items_count': cart.total_items,
            'cart_total': float(cart.total_amount),
        })
    except Cart.DoesNotExist:
        return JsonResponse({'cart_items_count': 0, 'cart_total': 0})
