from django.urls import path,include
from . import views
urlpatterns = [ 
       path('all-transactions',views.all_transactions,name="all-transactions")
]