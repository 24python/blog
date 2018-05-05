from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth  # auth模块
# from app01.models import UserInfo  # 注册创建用户要用到
from django.http import JsonResponse
from PIL import Image
from PIL import ImageDraw, ImageFont
from io import BytesIO
import random
from app01.models import *
from django import forms
from django.forms import widgets
from django.core.exceptions import  ValidationError
import json
from django.db import transaction
from django.db.models import F
import os
from cnblogs import settings


# Create your views here.


# 登录函数
def login(request):
    if request.is_ajax():
        user = request.POST.get("user")
        print(user)
        pwd = request.POST.get("pwd")
        print(pwd)
        valid_code = request.POST.get("valid_code")
        res = {"state": False, "msg": None}

        valid_str = request.session.get("valid_str")

        if valid_code.upper() == valid_str.upper():
            user = auth.authenticate(username=user, password=pwd)
            if user:
                res["state"] = True
                auth.login(request, user)

            else:
                res["msg"] = "userinfo or pwd error"
        else:
            res["msg"] = "验证码错误"

        return JsonResponse(res)

    return render(request, "login.html")


# 生成随机图片背景颜色
def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


# 生成随机验证图片
def get_valid_img(request):
    image = Image.new("RGB", (250, 40), get_random_color())

    # 生成五个随机字符
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(r'C:\Users\Administrator\PycharmProjects\cnblogs\static\font\kumo.ttf', size=32)
    temp = []
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_low_alpha = chr(random.randint(97, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        draw.text((24 + i * 36, 0), random_char, get_random_color(), font=font)

        # 保存随机字符
        temp.append(random_char)

    # 在内存生成图片
    f = BytesIO()
    image.save(f, "png")
    data = f.getvalue()
    f.close()

    # ["a","2","2","s"]
    valid_str = "".join(temp)  # "a22s"
    print("valid_str", valid_str)

    request.session["valid_str"] = valid_str

    return HttpResponse(data)


def long_out(request):
    auth.logout(request)
    return redirect("/login/")


# 修改密码
def set_pwd(request):
    if request.method == "POST":
        oldpassword = request.POST.get("oldpassword")
        newpassword = request.POST.get("newpassword")
        # 得到当前登录的用户，判断旧密码是不是和当前的密码一样
        username = request.user  # 打印的是当前登录的用户名
        user = UserInfo.objects.get(username=username)  # 查看用户
        ret = user.check_password(oldpassword)  # 检查密码是否正确
        if ret:
            user.set_password(newpassword)  # 如果正确就给设置一个新密码
            user.save()  # 保存
            return redirect("/login/")
        else:
            info = "输入密码有误"
            return render(request, "set_pwd.html", {"info": info})
    return render(request, "set_pwd.html")


# form组件设置校验规则
class RegForm(forms.Form):
    user = forms.CharField(max_length=8, label="用户名",
                           widget=widgets.TextInput(attrs={"class": "form-control"})
                           )
    pwd = forms.CharField(min_length=4, label="密码",
                          widget=widgets.PasswordInput(attrs={"class": "form-control"})
                          )
    repeat_pwd = forms.CharField(min_length=4, label="确认密码",
                                 widget=widgets.PasswordInput(attrs={"class": "form-control"})
                                 )
    email = forms.EmailField(label="邮箱",
                             widget=widgets.EmailInput(attrs={"class": "form-control"})
                             )

    def clean_user(self):
        val = self.cleaned_data.get("user")
        # val=self.cleaned_data.get("pwd")

        ret = UserInfo.objects.filter(username=val)
        if not ret:
            return val
        else:
            raise ValidationError("该用户已存在")

    def clean(self):
        if self.cleaned_data.get("pwd") == self.cleaned_data.get("repeat_pwd"):
            return self.cleaned_data
        else:
            raise ValidationError("两次密码不一致！")


# 注册函数
def reg(request):
    if request.method == "POST":
        res = {"user": None, "error_dict": None}
        form = RegForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)  # {"user":"yuan","pwd":"12345","repeat_pwd":"12","email":"123"}
            print(request.FILES)

            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar = request.FILES.get("avatar")
            print("user", user)
            if avatar:
                user = UserInfo.objects.create_user(username=user, password=pwd, email=email, avatar=avatar)
            else:
                user = UserInfo.objects.create_user(username=user, password=pwd, email=email)

            res["user"] = user.username
        else:
            print(form.errors)  # {"repeat_pwd":["....",],"email":["......",]}
            print(form.cleaned_data)
            res["error_dict"] = form.errors
        return JsonResponse(res)

    # 生成一个未绑定数据的form实例对象
    form = RegForm()
    return render(request, "reg.html", locals())


# index函数
def index(request):
    article_list = Article.objects.all()

    return render(request, "index.html", {"article_list": article_list})


# 个人站点
def homesite(request, username, **kwargs):
    print("kwargs:", kwargs)

    print(username)
    # 当前站点用户对象
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    # 当前站点对象
    blog = user.blog

    # 查询当前站点的所有文章

    if not kwargs:
        article_list = Article.objects.filter(user=user)
    else:
        condition = kwargs.get("condition")
        param = kwargs.get("param")
        if condition == "cate":
            article_list = Article.objects.filter(user=user).filter(category__title=param)
        elif condition == "tag":
            article_list = Article.objects.filter(user=user).filter(tags__title=param)
        else:
            print(param)
            year, month = param.split("-")
            article_list = Article.objects.filter(user=user).filter(create_time__year=2018, create_time__month=4)

    return render(request, "homesite.html", locals())


def article_detail(request, username, article_id):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog

    article = Article.objects.filter(pk=article_id).first()

    comment_list = Comment.objects.filter(article_id=article_id)
    return render(request, "article_detail.html", locals())


# 点赞
def poll(request):
    print(request.POST)
    is_up = json.loads(request.POST.get("is_up"))
    print(is_up)
    article_id = request.POST.get("article_id")
    user_id = request.user.pk

    res = {"state": True}

    try:
        with transaction.atomic():
            ArticleUpDown.objects.create(is_up=is_up, article_id=article_id, user_id=user_id)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)

    except Exception as e:
        res["state"] = False
        res["first_operate"] = ArticleUpDown.objects.filter(article_id=article_id, user_id=user_id).first().is_up

    return JsonResponse(res)


def comment(request):
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    pid = request.POST.get("pid")
    user_id = request.user.pk

    res = {"state": True}

    with transaction.atomic():
        if not pid:  # 提交根评论
            obj = Comment.objects.create(user_id=user_id, article_id=article_id, content=content, )
        else:  # 提交子评论
            obj = Comment.objects.create(user_id=user_id, article_id=article_id, content=content, parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    res["time"] = obj.create_time.strftime("%Y-%m-%d %H:%M")
    res["content"] = obj.content

    return JsonResponse(res)


def get_comment_tree(request, id):
    ret = list(Comment.objects.filter(article_id=id).values("pk", "content", "parent_comment_id", "user__username"))

    return JsonResponse(ret, safe=False)


def backend(request):
    users = request.user.username
    print(users)

    user = UserInfo.objects.filter(username=users).first()
    if not user:
        return HttpResponse("404")
    # 当前站点对象
    blog = user.blog
    # 查询当前站点的所有文章

    article_list = Article.objects.filter(user=user)

    return render(request, "backend.html",locals())


def add_article(request):
    if request.method == "POST":
        print(request.POST.get("title"))
        print(request.POST)
        print(request.POST.get("article_con"))
        title = request.POST.get("title")
        article_con = request.POST.get("article_con")
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(article_con, "html.parser")
        print("text1", soup)
        # 过滤
        for tag in soup.find_all():
            if tag.name == "script":
                tag.decompose()

        print("text2", soup)

        article_obj = Article.objects.create(title=title, user=request.user, desc=soup.text[0:150])
        ArticleDetail.objects.create(content=soup.prettify(), article=article_obj)

        return HttpResponse("提交成功")
    else:
        return render(request, "add_article.html")


def upload_img(request):
    print(request.POST)
    print(request.FILES)
    img_obj = request.FILES.get("img")

    media_path = settings.MEDIA_ROOT
    path = os.path.join(media_path, "article_imgs", img_obj.name)
    f = open(path, "wb")

    for line in img_obj:
        f.write(line)
    f.close()

    res = {
        "url": "/media/article_imgs/" + img_obj.name,
        "error": 0
    }

    return HttpResponse(json.dumps(res))

def delete_student(request):
    # 取到前端页面传过来的数据的ID值
    delete_id = request.GET.get("id")
    # 根据ID值去数据库取到相应的数据
    student_obj = Article.objects.get(id=delete_id)
    # 删除
    student_obj.delete()

    return redirect("/student_index/")
def edit_article(request):
    if request.method == "POST":
        # 取到编辑后的信息，更新到数据库
        id = request.POST.get("nid")

        # 更新当前编辑的对象
        obj = models.Arteacher.objects.get(nid=id)
        obj.save()

        return redirect("/teacher_index/")

        # 取到要编辑的当前信息
    edit_id = request.GET.get("nid")
    # 取对应的数据
    obj = models.Article.objects.get(nid=edit_id)

    # 取到所有的班级
    data = tinyMCE.activeEditor.getContent()
    return render(request, "edit_article.html", {"teacher": obj, "class_list": data})
