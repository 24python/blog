# by luffycity.com



from django import template
register=template.Library()


@register.simple_tag
def mul(x,y):
    return x*y


from ..models import *


@register.inclusion_tag("menu.html")
def get_menu(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # 查询当前站点的所有分类
    cate_list = Category.objects.filter(blog=blog)
    print(cate_list)
    # 查询每一个分类名称以及对应的文章数
    from django.db.models import Count
    cate_list = Category.objects.filter(blog=blog).annotate(c=Count("article")).values_list("title", "c")
    print(cate_list)
    # 查询每一个标签以及对应的文章数
    tag_list = Tag.objects.filter(blog=blog).annotate(c=Count("article")).values_list("title", "c")
    print(tag_list)
    # 查询每一个年月和对应的文章数
    date_list = Article.objects.filter(user=user).extra(
        select={"create_ym": "DATE_FORMAT(create_time,'%%Y-%%m')"}).values("create_ym").annotate(
        c=Count("nid")).values_list("create_ym", "c")
    print(date_list)

    return {"username":username,"cate_list":cate_list,"tag_list":tag_list,"date_list":date_list}