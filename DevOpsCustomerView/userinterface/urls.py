from . import views
from django.urls import path


urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.loggingout, name='logout'),
    path('overview/', views.projectList, name='overview'),
    path('reports/', views.reportsOverview, name='reportsOverview'),    
    path('project/<slug:slug>/<int:id>', views.projectView, name='project'),
    path('project/<slug:slug>/<int:id>/<str:hash>', views.projectPublic, name='publicOverview'),
    path('project/<slug:slug>/<int:id>/print/<str:date>', views.printOverview, name='printOverview'),
    path('project/<slug:slug>/<int:id>/documentation/', views.wiki, name='wiki'),
    path('project/<slug:slug>/<int:id>/downloads/', views.fileList, name='downloads'),
    path('project/<slug:slug>/<int:id>/download/<str:file>', views.fileDownload, name='download'),
    path('project/<slug:slug>/<int:id>/documentation/print/', views.printWiki, name='printWiki'),
    path('project/<slug:slug>/<int:id>/documentation/<path:page>', views.wikiPage, name='wikiPage'),
    path('project/<slug:slug>/<int:id>/issues/', views.issueList, name='issueList'),
    path('project/<slug:slug>/<int:id>/issues/create', views.issueCreate, name='issueCreate'),
    path('project/<slug:slug>/<int:id>/issues/<int:issue>', views.issue, name='issue'),
    path('project/<slug:slug>/<int:id>/milestones/', views.milestones, name='milestones'),
    path('project/<slug:slug>/<int:id>/milestone/<int:mid>', views.milestoneBoard, name='milestoneBoard'),
    path('cache/clear/', views.clearCache, name='clearCache'),
    path('cache/warmup/', views.warmupCache, name='warmupCache'),
]