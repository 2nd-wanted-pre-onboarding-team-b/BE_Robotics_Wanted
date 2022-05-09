from django.shortcuts import render
from rest_framework import status, mixins, generics
from restaurants.models import Restaurant
from restaurants.serializers import RestaurantSerializer

class RestuarantsCreateView(generics.GenericAPIView,
                            mixins.CreateModelMixin):
    """
    작성자: 하정현
    식당 생성 View

    (POST) /api/restaurants/create
    """
    serializer_class = RestaurantSerializer
    def post(self, request):
        return self.create(request)


class RestaurantsView(generics.GenericAPIView,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):
    """
    작성자: 하정현
    식당 정보에 대한 View

    (GET)       /api/restaurants/<int:id>
    (PATCH)     /api/restaurants/<int:id>
    (DELETE)    /api/restaurants/<int:id>
    """

    lookup_field = 'id'
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.all()

    def get(self, request, id):
        return self.retrieve(request, id)
    
    def patch(self, request, id):
        return self.update(request, id, partial=True)

    def delete(self, request, id):
        return self.destroy(request, id)