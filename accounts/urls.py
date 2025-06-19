from django.urls import path,include
from . import views
urlpatterns = [
    path('register/',views.register,name="register"),
    path('login/',views.login_view,name="login"),
    path('logout/',views.logout_view,name="logout"),
    path('client-login/',views.client_login_view,name="client-login"),
]
