

"""
URL configuration for greatkart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import statistics
from django.conf import settings
from django.contrib import admin
from django.urls import path
from greatkart import views
from greatkart.settings import MEDIA_ROOT
from django.conf.urls.static import static
from store import views

urlpatterns = [
    path('',views.store,name = 'store'),
    path('category/<slug:category_slug>/',views.store,name = 'products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detail,name = 'product_detail'),
    path('search/',views.search,name = 'search'),
    path('submit_review/<int:product_id>/',views.submit_review,name="submit_review")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
