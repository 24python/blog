from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Article)
admin.site.register(Article2Tag)
admin.site.register(ArticleDetail)
admin.site.register(ArticleUpDown)
admin.site.register(Category)
admin.site.register(UserInfo)
admin.site.register(Tag)
admin.site.register(Blog)
admin.site.register(Comment)