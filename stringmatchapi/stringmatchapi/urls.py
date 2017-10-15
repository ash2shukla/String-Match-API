from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from serve.views import bulkview,subprojectview,mapprojects,indexview,collectionview,collectioninsert,no_objection
urlpatterns = [
    url(r'^search/', indexview, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^projectin/',collectioninsert),
    url(r'^projectlist/',collectionview),
    url(r'^subprojectlist/',subprojectview),
    url(r'^subprojectin/',mapprojects),
    url(r'^insert/',no_objection),
    url(r'^insertBulk/',bulkinsert),
    url(r'^getbulk/',bulkview)
]
