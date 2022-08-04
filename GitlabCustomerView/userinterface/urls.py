from . import views
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('', views.index, name='index'),
    path('overview/', views.overview, name='overview'),
    path('project/<slug:slug>/<int:id>', views.project, name='project'),
    path('project/<slug:slug>/<int:id>/documentation/', views.wiki, name='wiki'),
    path('project/<slug:slug>/<int:id>/documentation/<path:page>', views.wikipage, name='wikipage'),
    path('project/<slug:slug>/<int:id>/issues/', views.issues, name='issues'),
    path('project/<slug:slug>/<int:id>/milestones/', views.milestones, name='milestones'),
    path('admin/', admin.site.urls),
]
