from django.urls import path
from django.conf.urls import url, include
from . import views
from .models import Question 
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ['question_text']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = UserSerializer

router = routers.DefaultRouter()
router.register(r'question',UserViewSet)

app_name = "polls"
urlpatterns = [
    url(r'^api',include(router.urls)),
    path('',views.index,name='index'),
    path ('<int:question_id>/', views.detail,name='detail'),
    path('<int:question_id>/results/', views.results,name='results'),
    path('<int:question_id>/vote/',views.vote, name= 'vote'),
    path('portal/<str:query>/',views.qaserver,name="qaserver"),
    #path('json/<str:query>/',views.qaserver_json,name="qaserver_json")
    path('post/',views.qaserver_json,name="qaserver_json")
]
