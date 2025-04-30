from django.urls import path,include
from . import views
urlpatterns = [ 
       
    path("draft-loan/<int:lender_id>/<str:unique_id>/", views.draft_loan, name="draft-loan"),
    path("new-loan/<int:lender_id>/<str:unique_id>/", views.loan_request, name="new-loan"),
    path('loan-request-list/',views.loan_request_list,name="loan-request-list"),
    path('accept-reject-status/<int:loan_id>/',views.accept_reject_status,name="accept-reject-status"),
    path('accepted-list/',views.accepted_list,name="accepted-list"),
    path('cancle-loan/<int:loan_id>/',views.cancle_loan,name="cancle-loan"),
    path('reject-loan/<int:loan_id>/',views.reject_loan,name="reject-loan"),
    path('payment-details/<int:loan_id>/',views.payment_details,name="payment-details"),
    path('cancel-reject-list',views.cancel_reject_list,name="cancel-reject-list"),
    path('paymentdone/<int:loan_id>/',views.paymentdone,name="paymentdone"),
    path('payment-done-check/<int:loan_id>/',views.payment_done_check,name="payment-done-check"),
    path('payment-done-list/',views.payment_done_list,name="payment-done-list"),
    path('paymentreceived/<int:loan_id>/',views.paymentreceived,name="paymentreceived"),
    path('loan-status-records',views.loan_status_records,name="loan-status-records"),
    path('delete_loan_item_image/<int:image_id>/',views.delete_loan_item_image,name="delete_loan_item_image"),
    path('generate-loan-agreement/<int:loan_id>', views.generate_pdf, name='generate-loan-agreement'),
] 