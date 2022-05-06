from django.urls import path

from .views import MenuViewSet, MenuSalesView


menu_list = MenuViewSet.as_view({
    "get" : "list",
    "post" : "create"
})

menu_detail = MenuViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', menu_list),
    path('/<int:pk>', menu_detail),
    path('/sales', MenuSalesView.as_view()),
]