from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>', views.UsernameProfileView.as_view(), name='profile'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('profile/<str:username>/', views.UsernameProfileView.as_view(), name='username_profile'),
    path('google-callback-signup/', views.GoogleRegisterView.as_view(), name='google_callback_signup'),
    path('google-callback-login/', views.GoogleLoginView.as_view(), name='google_callback_login'),
    path('partial-update/', views.UserPartialUpdateAPI.as_view(), name='partial_update'),
    path('favorite/', views.MarkFavourite.as_view(), name='favorite'),
]
