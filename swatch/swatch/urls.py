"""swatch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from views import signup_view
from views import homepage_view
from views import login_view,feed_view,post_view,comment_view,like_view
from . import views
urlpatterns = [	
		#.....the rest of your urlconf goes here....
    url(r'^admin/', admin.site.urls),
    url(r'^home/',homepage_view),
    url(r'^signup/',signup_view),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    url(r'^login/',login_view),
    url(r'^feed/',feed_view),
    url(r'^post/',post_view),
    url(r'^like/', like_view),
    url(r'^comment/',comment_view)
    
] 
