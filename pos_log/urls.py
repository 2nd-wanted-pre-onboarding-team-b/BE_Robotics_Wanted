from django.urls import path
from pos_log.views import PoslogListView

urlpatterns = [
    path('', PoslogListView.as_view()),
]