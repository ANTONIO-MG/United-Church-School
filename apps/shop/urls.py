"""HTML routes for the shop (mounted at ``/shop/`` under the ``shop`` namespace)."""

from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    # Storefront (buyers)
    path('', views.storefront, name='storefront'),
    path('product/<int:pk>/', views.product_detail, name='product-detail'),

    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add-to-cart'),
    path('cart/item/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/coupon/', views.apply_coupon, name='apply-coupon'),

    path('download/<int:pk>/', views.download_product, name='download-product'),
    path('download/<int:pk>/<int:file_id>/', views.download_file, name='download-file'),
    path('orders/', views.my_orders, name='my-orders'),
    path('bookings/', views.my_bookings, name='my-bookings'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('orders/<int:pk>/', views.order_detail, name='order-detail'),

    # Catalogue management (staff)
    path('manage/products/', views.all_products, name='all-products'),
    path('manage/products/add/', views.add_product, name='add-product'),
    path('manage/products/<int:pk>/edit/', views.edit_product, name='edit-product'),
    path('manage/products/<int:pk>/delete/', views.delete_product, name='delete-product'),
    path('manage/fulfilment/', views.fulfilment, name='fulfilment'),
    path('manage/fulfilment/<int:pk>/', views.fulfilment_action, name='fulfilment-action'),
    path('manage/fulfilment/<int:pk>/waybill/', views.waybill, name='waybill'),
    path('manage/fulfilment/<int:pk>/slip/', views.packing_slip, name='packing-slip'),
    path('manage/educators/', views.educators, name='educators'),
    path('manage/educators/<int:person_id>/', views.educator_hours, name='educator-hours'),
    path('manage/discounts/', views.discounts, name='discounts'),
    path('manage/discounts/add/', views.add_discount, name='add-discount'),
    path('manage/discounts/<int:pk>/edit/', views.edit_discount, name='edit-discount'),
    path('manage/discounts/<int:pk>/delete/', views.delete_discount, name='delete-discount'),
    path('manage/categories/', views.categories, name='categories'),
    path('manage/categories/<int:pk>/delete/', views.delete_category, name='delete-category'),
]
