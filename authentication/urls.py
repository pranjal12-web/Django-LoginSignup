
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
path('', views.home,name="home"),#url for the home page
path('signup', views.signup,name="signup"),#url for the signup page
path('signin', views.signin,name="signin"),#url for the signin page
path('signout', views.signout,name="signout"),#url for the signout page
path('activate/<uidb64>/<token>', views.activate,name="activate")
]