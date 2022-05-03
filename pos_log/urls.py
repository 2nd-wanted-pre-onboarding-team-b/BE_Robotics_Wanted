from django.urls import path
from pos_log.views import PoslogListView, PosLogSearcherView

urlpatterns = [
    path(r'/<str:search_type>', PosLogSearcherView.as_view()),
    path('', PoslogListView.as_view()),
]