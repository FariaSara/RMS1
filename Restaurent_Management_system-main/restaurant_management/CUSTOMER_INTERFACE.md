# Customer Interface Documentation

## Overview

The customer interface allows customers to browse the restaurant menu, add items to their cart, and place orders. It's designed to be user-friendly and responsive across all devices.

## Features

### Customer Features
- **Menu Browsing**: View menu items organized by categories (Appetizers, Main Courses, Soups, Desserts, Beverages)
- **Category Filtering**: Filter menu items by category
- **Shopping Cart**: Add items to cart, adjust quantities, remove items
- **Order Placement**: Place orders with customer information
- **Order Tracking**: Track order status in real-time
- **Order Types**: Support for both dine-in and takeaway orders

### Admin Features
- **Order Management**: View and manage customer orders
- **Status Updates**: Update order status through the admin interface
- **Order Filtering**: Filter orders by status, type, and search by customer details
- **Dashboard Integration**: Customer orders appear in the main dashboard

## URL Structure

### Customer URLs
- `/customer/` - Main menu page
- `/customer/cart/` - Shopping cart
- `/customer/checkout/` - Checkout page
- `/customer/order-confirmation/<order_number>/` - Order confirmation
- `/customer/track-order/` - Order tracking

### Admin URLs
- `/customer/admin/orders/` - Customer order management

## Models

### Customer
- User information (name, email, phone, address)
- Can be linked to Django User accounts

### Cart & CartItem
- Session-based shopping cart
- Supports guest users
- Automatic cart persistence

### CustomerOrder & CustomerOrderItem
- Complete order information
- Order status tracking
- Integration with existing admin system

## Order Status Flow

1. **Pending** - Order received, awaiting confirmation
2. **Confirmed** - Order confirmed by restaurant
3. **Preparing** - Order being prepared by kitchen
4. **Ready** - Order ready for pickup/serving
5. **Completed** - Order completed
6. **Cancelled** - Order cancelled

## Menu Categories

The system supports the following menu categories:
- **Appetizers** - Starters and small plates
- **Main Courses** - Main dishes and entrees
- **Soups** - Soup varieties
- **Desserts** - Sweet treats and desserts
- **Beverages** - Drinks and beverages
- **Salads** - Fresh salads
- **Sides** - Side dishes

## Installation & Setup

1. **Migrations**: The system automatically creates necessary database tables
2. **Sample Data**: Sample menu items and categories are included
3. **Admin Integration**: Customer orders appear in the existing admin dashboard

## Usage

### For Customers

1. **Browse Menu**: Visit `/customer/` to view the menu
2. **Add to Cart**: Click "Add to Cart" on desired items
3. **Manage Cart**: Adjust quantities or remove items in the cart
4. **Checkout**: Provide customer information and place order
5. **Track Order**: Use the order number to track order status

### For Restaurant Staff

1. **View Orders**: Access customer orders through the admin interface
2. **Update Status**: Change order status as orders progress through kitchen
3. **Monitor Dashboard**: Customer orders appear in the main dashboard metrics

## Technical Details

### Frontend Technologies
- **Tailwind CSS** - For responsive, modern styling
- **Font Awesome** - For icons
- **Vanilla JavaScript** - For interactive functionality
- **AJAX** - For real-time cart updates

### Backend Features
- **Session-based Carts** - No login required for customers
- **Atomic Transactions** - Ensures data consistency during order placement
- **Admin Integration** - Seamless integration with existing admin system
- **RESTful APIs** - For cart management and updates

### Security
- **CSRF Protection** - All forms are CSRF protected
- **Input Validation** - Server-side validation for all inputs
- **Session Security** - Secure session handling for guest carts

## Customization

### Styling
- Customer interface uses a separate base template with restaurant-specific branding
- Colors and styling can be customized in the base template
- Responsive design works on all device sizes

### Categories
- Menu categories can be added/modified through the Django admin
- Each category has a type, description, and display order
- Categories can be activated/deactivated

### Order Flow
- Order statuses can be customized in the CustomerOrder model
- Email notifications can be added for order updates
- Integration with payment systems can be added

## Future Enhancements

- **User Accounts** - Allow customers to create accounts for order history
- **Payment Integration** - Add online payment processing
- **Email Notifications** - Send order confirmations and updates via email
- **SMS Notifications** - Send order status updates via SMS
- **Loyalty Program** - Implement customer loyalty and rewards
- **Reviews & Ratings** - Allow customers to rate menu items
- **Mobile App** - Create a mobile app version

## Support

For technical support or questions about the customer interface, please refer to the Django admin documentation or contact the development team.