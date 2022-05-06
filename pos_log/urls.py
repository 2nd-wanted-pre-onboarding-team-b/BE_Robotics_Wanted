from django.urls import path
from pos_log.views import PosLogSearchView

urlpatterns = [
    path('', PosLogSearchView.as_view()),
]