from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('check-fingerprint/', views.check_fingerprint_and_send_form, name = 'check_fingerprint'),
    path('save-fingerprint/', views.save_fingerprint, name = 'save_fingerprint'),
    path('update-overview/', views.update_overview, name = 'update_overview'),
    path('update-socioeconomic-dimension/', views.update_socioeconomic_dimension, name = 'update_socioeconomic_dimension'),
    path('update-environment-dimension/', views.update_environment_dimension, name = 'update_environment_dimension'),
    path('results/', views.results, name = 'results'),
    path('evaluator/', views.evaluator, name = 'evaluator'),
    path('tutorial/', views.tutorial, name = 'tutorial')
]
