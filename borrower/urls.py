from django.urls import path,include
from . import views
urlpatterns = [

    path("change-password/", views.change_client_password, name="change-client-password"),
    path("dashboard/", views.client_dashboard, name="client-dashboard"),

    path('client-new-loan',views.client_new_loan,name="client-new-loan"),

]