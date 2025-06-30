from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from pekerjaan import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 Login & Logout
    path('login/', auth_views.LoginView.as_view(template_name='pekerjaan/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Aplikasi utama
    path('', views.input_pekerjaan, name='input_pekerjaan'),
    path('view/', views.view_data, name='view_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/<int:id>/', views.edit_data, name='edit_data'),
    path('delete/<int:id>/', views.delete_data, name='delete_data'),
    path('pekerjaan/rincian/', views.rincian_pekerjaan, name='rincian_pekerjaan'),
]
