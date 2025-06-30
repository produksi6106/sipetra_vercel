from django.urls import path
from . import views

urlpatterns = [
    path('', views.input_pekerjaan, name='input_pekerjaan'),
    path('view/', views.view_data, name='view_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/<int:id>/', views.edit_data, name='edit_data'),
    path('delete/<int:id>/', views.delete_data, name='delete_data'),
    path('rincian/', views.rincian_pekerjaan, name='rincian_pekerjaan'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
