from django.conf.urls import url
from app01 import views

urlpatterns = [
    # 后台管理
    url("backend/$", views.backend, ),
    url("add_article/$", views.add_article, ),
    url(r'^edit_article', views.edit_article),



    url("poll/$", views.poll, ),
    url("comment/$", views.comment, ),
    url("get_comment_tree/(\d+)$", views.get_comment_tree, ),


    url("(?P<username>\w+)/(?P<condition>tag|cate|achrive)/(?P<param>.*)", views.homesite, ),
    # homesite(request,username="egon",condition="cate",param="python")
    url("(?P<username>\w+)/articles/(?P<article_id>\d+)/$", views.article_detail, ),

    url("(?P<username>\w+)/$", views.homesite, name='aaa'),  # homesite(request)

]