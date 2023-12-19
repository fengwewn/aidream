"""AiDream URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include, re_path
from AiDream import views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('',views.home),
    path('register',views.register),
    path('registerConfirm',views.registerConfirm),
    path('login',views.login),
    path('logout',views.logout),
    path('resetPassword',views.resetPassword),
    path('home',views.home),

    path('addEmbeddingTask',views.addEmbeddingTask),
    path('addGenerateTask',views.addGenerateTask),

    path('uploadImage',views.uploadImage),
    path('delEmbedding',views.delEmbedding),


    path('showGenerateImage',views.showGenerateImage),
    path('getGenerateImage',views.getGenerateImage),
    path('downloadGenerateImage',views.downloadGenerateImage),

    path('chatgptTagGenerate',views.chatgptTagGenerate),

    path('captcha/',include('captcha.urls')),
    path('refresh_captcha',views.refresh_captcha),

]
