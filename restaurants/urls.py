from django.contrib import admin
from django.urls import path
from restaurants.models import Restaurant

from restaurants.views import RestuarantsCreateView, RestaurantsView

urlpatterns = [
    path('/create', RestuarantsCreateView.as_view()),
    path('/<int:id>', RestaurantsView.as_view())
]
