from django.urls import path

from . import views

app_name = "properties"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.SearchResultsView.as_view(), name="search"),
    path("property/<slug:slug>/", views.PropertyDetailView.as_view(), name="detail"),
]
