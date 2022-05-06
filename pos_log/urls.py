from django.urls import path
from pos_log.views import PosLogSearchView, PoslogListView, PoslogDetailView

urlpatterns = [
    path('/search', PosLogSearchView.as_view()),
    path('', PoslogListView.as_view()),
    path('<int:pos_id>', PoslogDetailView.as_view()) 
]