from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()


# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),
from serve.views import indexview,collectionview,collectioninsert,no_objection
urlpatterns = [
    url(r'^search/', indexview, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^projectin/',collectioninsert),
    url(r'^projectlist/',collectionview),
    url(r'^insert/',no_objection)
]
