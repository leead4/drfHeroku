
from django.conf.urls import url, include
from rest_framework import routers
from api import views
from api.views import FileUploadView, CreateCardViewSet, GetCardsByDeckViewSet, CreateDeckViewSet, DeleteCardByIdViewSet, DeleteDeckByIdViewSet, EditCardViewSet

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'decks', views.DeckViewSet)
router.register(r'cards', views.CardViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^upload/', FileUploadView.as_view()),
    url(r'^createcard/', CreateCardViewSet.as_view()),
    url(r'^createdeck/', CreateDeckViewSet.as_view()),
    url(r'^getcardsindeck/(?P<deck_id>[0-9]+)/$', GetCardsByDeckViewSet.as_view()),
    url(r'^deletethiscard/(?P<card_id>[0-9]+)/$', DeleteCardByIdViewSet.as_view()),
    url(r'^deletethisdeck/(?P<deck_id>[0-9]+)/$', DeleteDeckByIdViewSet.as_view()),
    url(r'^editthiscard/(?P<card_id>[0-9]+)/$', EditCardViewSet.as_view())
]