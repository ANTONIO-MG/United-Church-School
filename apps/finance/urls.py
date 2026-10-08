"""HTML routes for finance (mounted at ``/finance/`` under the ``finance`` namespace)."""

from django.urls import path

from . import views, views_books as books, views_reports as dash

app_name = 'finance'

urlpatterns = [
    path('', views.invoices, name='invoices'),
    path('due/', views.due_payments, name='due-payments'),
    path('payments/', views.payment_history, name='payment-history'),
    # Proof of payment + manual access granting (admin/staff)
    path('payments/grant-access/', views.grant_access, name='grant-access'),
    path('payments/student/<int:person_id>/', views.student_payments, name='student-payments'),
    path('payments/proof/<int:pk>/', views.proof_document, name='proof-document'),
    path('invoice/<int:pk>/', views.invoice_detail, name='invoice-detail'),
    path('invoice/<int:pk>/receipt/', views.receipt, name='receipt'),
    path('invoice/<int:pk>/pdf/', views.invoice_pdf, name='invoice-pdf'),
    path('invoice/<int:pk>/receipt.pdf', views.receipt_pdf, name='receipt-pdf'),

    # Cart checkout + PayFast
    path('checkout/', views.checkout, name='checkout'),
    path('pay/<uuid:public_id>/', views.pay, name='pay'),
    path('payfast/notify/', views.payfast_notify, name='payfast-notify'),
    path('payfast/return/', views.payfast_return, name='payfast-return'),
    path('payfast/cancel/', views.payfast_cancel, name='payfast-cancel'),

    # Staff management
    path('register/', views.invoice_register, name='invoice-register'),
    path('overview/', dash.reports_home, name='money-overview'),
    path('my/', dash.my_finances, name='my-finances'),
    path('reports/', dash.reports_home, name='reports'),
    path('reports/<slug:slug>/', dash.report, name='report'),
    path('manage/add/', books.invoice_new, name='add-invoice'),
    path('manage/create/', views.create_invoice, name='create-invoice'),
    path('manage/<int:pk>/edit/', books.invoice_edit, name='edit-invoice'),
    path('manage/<int:pk>/delete/', views.delete_invoice, name='delete-invoice'),
    path('manage/<int:pk>/send/', views.send_invoice, name='send-invoice'),
    path('from-order/<int:order_id>/', views.generate_from_order, name='generate-from-order'),

    # Wave-style documents
    path('invoice/new/', books.invoice_new, name='invoice-new'),
    path('invoice/<int:pk>/edit/', books.invoice_edit, name='invoice-edit'),
    path('invoice/<int:pk>/action/', books.invoice_action, name='invoice-action'),
    path('estimates/', books.estimates, name='estimates'),
    path('estimates/new/', books.estimate_new, name='estimate-new'),
    path('estimates/<int:pk>/', books.estimate_detail, name='estimate-detail'),
    path('estimates/<int:pk>/edit/', books.estimate_edit, name='estimate-edit'),
    path('estimates/<int:pk>/pdf/', books.estimate_pdf, name='estimate-pdf'),
    # Under pay/ so the login and onboarding gates already let customers through.
    path('pay/estimate/<uuid:public_id>/', books.estimate_public, name='estimate-public'),
    path('pay/estimate/<uuid:public_id>/pdf/', books.estimate_public_pdf, name='estimate-public-pdf'),
    path('statement/', books.statement, name='statement'),
    path('statement/<int:user_id>/', books.statement, name='statement-for'),

    # Expenses
    path('expenses/', books.expenses, name='expenses'),
    path('expenses/add/', books.expense_form, name='expense-add'),
    path('expenses/<int:pk>/', books.expense_form, name='expense-edit'),
    path('expenses/<int:pk>/delete/', books.expense_delete, name='expense-delete'),
    path('expenses/<int:pk>/receipt/', books.expense_receipt, name='expense-receipt'),
    path('expenses/recurring/', books.recurring, name='recurring'),
    path('expenses/recurring/<int:pk>/', books.recurring_form, name='recurring-edit'),
    path('expenses/setup/', books.expense_setup, name='expense-setup'),
]
