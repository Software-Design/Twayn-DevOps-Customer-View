from . import views
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logginout, name='logout'),
    path('overview/', views.overview, name='overview'),
    path('project/<slug:slug>/<int:id>', views.project, name='project'),
    path('project/<slug:slug>/<int:id>/documentation/', views.wiki, name='wiki'),
    path('project/<slug:slug>/<int:id>/documentation/<path:page>', views.wikipage, name='wikipage'),
    path('project/<slug:slug>/<int:id>/issues/', views.issueList, name='issueList'),
    path('project/<slug:slug>/<int:id>/issues/create', views.issueCreate, name='issueCreate'),
    path('project/<slug:slug>/<int:id>/issues/<int:issue>', views.issue, name='issue'),
    path('project/<slug:slug>/<int:id>/milestones/', views.milestones, name='milestones'),
    path('cache/clear/', views.clearCache, name='clearCache'),
    path('cache/warmup/', views.warmupCache, name='warmupCache'),
    path('admin/', admin.site.urls),
]
