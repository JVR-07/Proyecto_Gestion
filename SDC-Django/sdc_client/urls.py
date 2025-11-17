from django.urls import path
from . import views

# Importaciones de Simple JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Vistas de páginas
    path('', views.home, name='home'),
    path('login-page/', views.login_page, name='login'), # Página de 'primer login'
    path('register/', views.register, name='register'),
    path('auth/', views.auth, name='auth'), # Página de 'auth' (formulario)
    
    # Feeds
    path('create_post/', views.create_post, name='create_post'),
    path('donee_feed', views.donee_feed, name='donee_feed'),
    path('donor_feed', views.donor_feed, name='donor_feed'),
    path('institution_feed', views.institution_feed, name='institution_feed'),
    path('post/<int:post_id>/interact/', views.create_transaction, name='create_transaction'),

    # --- API Endpoints para Autenticación ---
    
    # Endpoint login
    path('api/login/', views.api_login_view, name='api_login'), 
    
    # Endpoints de Simple JWT (para refrescar tokens)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]