from django.urls import path
from pos_log.views import PoslogListView, PosLogSearcherView

urlpatterns = [
    path('2', PosLogSearcherView.as_view()),
    path('', PoslogListView.as_view()),
]