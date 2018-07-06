from django.contrib import admin
from django.urls import path
from rango.views import index
from rango.views import about
from rango.views import show_category,add_category,add_page,register,user_login,restricted,user_logout,search,track_url,like_category,suggest_category,auto_add_page
from django.urls import re_path
urlpatterns = [ re_path(r'^$', index, name='index'),
                re_path(r'about/$', about, name='about'),
                re_path(r'^add_category/$', add_category, name='add_category'),
                re_path(r'^category/(?P<category_name_slug>[\w\-]+)/$', show_category, name='show_category'),
                re_path(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', add_page, name='add_page'),
                re_path(r'^register/$', register, name='register'), # New pattern!
                re_path(r'^login/$', user_login, name='login'),
                re_path(r'^restricted/', restricted, name='restricted'),
                re_path(r'^logout/$', user_logout, name='logout'),
                re_path(r'search/$', search, name='search'),
                re_path(r'^goto/$', track_url, name='goto'),
                re_path(r'^like_category/$', like_category, name='like_category'),
                re_path(r'^suggest_category/$', suggest_category, name='suggest_category'),
                re_path(r'^auto_add_page/$', auto_add_page, name='auto_add_page'),
              ]
