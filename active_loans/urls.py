from django.urls import path,include
from . import views
urlpatterns = [

       path('montly-loans/',views.montly_loans,name="montly-loans"),
       path('weekly-loans/',views.weekly_loans,name="weekly-loans"),
       path('onetime-loans/',views.onetime_loans,name="onetime-loans"),
       path('all-loans/',views.all_loans,name="all-loans"),
       path('repayment-confirmation',views.repayment_confirmation,name='repayment-confirmation'),
       path('update-repayment-status/', views.update_repayment_status, name='update_repayment_status'),

]