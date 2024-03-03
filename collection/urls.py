from django.urls import path
from collection import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('movies/', views.get_movies, name='get_movies'),
    path('request-count/', views.RequestCountView.as_view(), name='request_count'),
    path('request-count/reset/', views.ResetRequestCountView.as_view(), name='reset_request_count'),
    path('collection/', views.CollectionListView.as_view(), name='cl_collection'), # create and list collections
    path('collection/<str:collection_uuid>/', views.CollectionDetailView.as_view(), name='rud_collection'), # get, update and delete collection
]