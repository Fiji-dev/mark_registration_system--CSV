from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('input_mark/', views.input_mark, name='input_mark'),  # Input marks page
    path('update_mark/', views.update_mark, name='update_mark'),  # Update marks page
    path('view_marks/', views.view_mark, name='view_marks'),  # View marks page
    path('visualization/', views.visualization, name='visualization'),
    path('get_stats/', views.get_stats, name='get_stats'),   
]
