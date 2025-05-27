from django.urls import path
from . import views
urlpatterns = [
    path('',views.dashboard,name="dashboard"),
    path('new-loan/',views.new_loan,name="new-loan"),
]