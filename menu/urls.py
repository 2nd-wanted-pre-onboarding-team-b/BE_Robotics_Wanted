from django.contrib import admin
from django.urls import path

from .views import MenuListView, MenuDetailView, BonusPointView, BonusPointMenuView

urlpatterns = [
    path('', MenuListView.as_view()),
    path('/<int:pk>', MenuDetailView.as_view()),
    path('/group', BonusPointView.as_view()),
    path('/comparison', BonusPointMenuView.as_view()),
]