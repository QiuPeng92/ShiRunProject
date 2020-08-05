# reverse模块用于反向解析url
from django.shortcuts import render, HttpResponse, redirect, reverse
from salary import forms
from salary import models
from django.http import JsonResponse
from django.contrib import auth
from salary import models
# 导入page模块
from salary.utils import page
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views import View
# 在Django中利用mark_safe,在模板中利用过滤器safe
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator
import datetime
from django.db.models import Count, F, Q, Sum
from decimal import Decimal
import xlwt
from io import BytesIO


# 主页视图函数(添加auth验证装饰器)
@login_required
def index(request):
    # 刷选今年的数据
    current_year = datetime.datetime.now().year
    # 过滤今年的数据
    currentyear_all_data = models.StaticInformation.objects.filter(deliver_time__year=current_year)
    ################################ 获取今年每月的数据
    current_month_data = currentyear_all_data.values("deliver_time__year", "deliver_time__month").annotate(
        c=Count(1)).values("deliver_time__month", "c").order_by("deliver_time__month")
    total_month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    current_month_data_list = []
    for i in list(current_month_data):
        current_month_data_list.append(i['deliver_time__month'])
    ret = []
    for i in total_month:
        if i not in current_month_data_list:
            ret2 = {}
            ret2["deliver_time__month"] = i
            ret2["c"] = 0
            ret.append(ret2)
    for i in list(current_month_data):
        ret.append(i)
    new_ret = sorted(ret, key=lambda e: e.__getitem__('deliver_time__month'))
    result_thisyear = []
    for i in new_ret:
        result_thisyear.append(i['c'])

    # 刷选去年的数据
    last_year = current_year - 1
    lastyear_all_data = models.StaticInformation.objects.filter(deliver_time__year=last_year)
    ################################ 获取去年每月的数据
    last_month_data = lastyear_all_data.values("deliver_time__year", "deliver_time__month").annotate(
        c=Count(1)).values("deliver_time__month", "c").order_by("deliver_time__month")
    last_month_data_list = []
    for i in list(last_month_data):
        last_month_data_list.append(i['deliver_time__month'])  # last_month_data_list=[12]
    ret_last = []
    for i in total_month:
        if i not in last_month_data_list:
            ret2 = {}
            ret2["deliver_time__month"] = i
            ret2["c"] = 0
            ret_last.append(ret2)
    for i in list(last_month_data):
        ret_last.append(i)
    new_ret_last = sorted(ret_last, key=lambda e: e.__getitem__('deliver_time__month'))
    result_lastyear = []
    for i in new_ret_last:
        result_lastyear.append(i['c'])
    # 未审批的个数
    information_notes = models.Information.objects.filter(status_audit=1).count()
    return render(request, "index.html", locals())


# 每月运费视图函数(添加auth验证装饰器)
@login_required
def freight(request):
    # 刷选今年的数据
    current_year = datetime.datetime.now().year
    # 过滤今年的数据
    currentyear_all_data = models.StaticInformation.objects.filter(deliver_time__year=current_year)
    ################################ 获取今年每月的数据
    current_month_data = currentyear_all_data.values("deliver_time__year", "deliver_time__month").annotate(
        sum=Sum(F("short_price") + F("long_price"))).values("deliver_time__month", "sum").order_by(
        "deliver_time__month")
    total_month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    current_month_data_list = []
    for i in list(current_month_data):
        current_month_data_list.append(i['deliver_time__month'])
    ret = []
    for i in total_month:
        if i not in current_month_data_list:
            ret2 = {}
            ret2["deliver_time__month"] = i
            ret2["sum"] = 0
            ret.append(ret2)
    for i in list(current_month_data):
        ret.append(i)
    new_ret = sorted(ret, key=lambda e: e.__getitem__('deliver_time__month'))
    result_thisyear = []
    for i in new_ret:
        result_thisyear.append(float(i['sum']))
    # print("result_thisyear", result_thisyear)

    # 刷选去年的数据
    last_year = current_year - 1
    lastyear_all_data = models.StaticInformation.objects.filter(deliver_time__year=last_year)
    ################################ 获取去年每月的数据
    last_month_data = lastyear_all_data.values("deliver_time__year", "deliver_time__month").annotate(
        sum=Sum(F("short_price") + F("long_price"))).values("deliver_time__month", "sum").order_by(
        "deliver_time__month")
    last_month_data_list = []
    for i in list(last_month_data):
        last_month_data_list.append(i['deliver_time__month'])  # last_month_data_list=[12]
    ret_last = []
    for i in total_month:
        if i not in last_month_data_list:
            ret2 = {}
            ret2["deliver_time__month"] = i
            ret2["sum"] = 0
            ret_last.append(ret2)
    for i in list(last_month_data):
        ret_last.append(i)
    new_ret_last = sorted(ret_last, key=lambda e: e.__getitem__('deliver_time__month'))
    result_lastyear = []

    for i in new_ret_last:
        result_lastyear.append(float(i['sum']))
    # 未审批的个数
    information_notes = models.Information.objects.filter(status_audit=1).count()
    return render(request, "freight.html", locals())


# 登录视图函数
def login(request):
    '''
    基于ajax和用户认证组件实现的登录功能
    :param request:
    :return:
    '''
    # 如果请求是ajax请求
    if request.is_ajax():
        # 获取post请求中对的username
        username = request.POST.get("username")
        # 获取post请求中对的password
        password = request.POST.get("password")
        # Ajax请求返回一个字典
        response = {"user": None, "err_msg": ""}
        # auth校验获取到的数据(如果效验通过则返回一个对象,如果不通过,则返回None)
        user_obj = auth.authenticate(username=username, password=password)
        # 如果通过auth效验
        if user_obj:
            # 向request中注册user_obj,则request.user就可以使用
            auth.login(request, user_obj)  # 等同于request.session["user_id"] = user_obj.pk
            response["user"] = username
        # 如果效验失败
        else:
            response["err_msg"] = "用户名或密码错误"
        return JsonResponse(response)
    return render(request, "login.html")


# 手机登录视图函数
def phone_login(request):
    '''
        基于ajax和用户认证组件实现的手机登录功能
        :param request:
        :return:
        '''
    # 如果请求是ajax请求
    if request.is_ajax():
        # 获取post请求中对的username
        username = request.POST.get("username")
        # 获取post请求中对的password
        password = request.POST.get("password")
        # Ajax请求返回一个字典
        response = {"user": None, "err_msg": ""}
        # auth校验获取到的数据(如果效验通过则返回一个对象,如果不通过,则返回None)
        user_obj = auth.authenticate(username=username, password=password)
        # 如果通过auth效验
        if user_obj:
            # 向request中注册user_obj,则request.user就可以使用
            auth.login(request, user_obj)  # 等同于request.session["user_id"] = user_obj.pk
            response["user"] = username
        # 如果效验失败
        else:
            response["err_msg"] = "用户名或密码错误"
        return JsonResponse(response)
    return render(request, "phone_login.html")


# 手机主页函数
@login_required(login_url="/phone/login/")
def phone_index(request):
    # 取到当前用户名
    username = request.user.username
    # 取到当前用户对象
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 获取当前****驾驶员****用户下所有的车辆
    car_list = user_obj.car_drivers.all()
    informantion_form = forms.PhoneInformationModelForm()
    if request.method == "POST":
        # 创建ModelForm对象,并将request.POST传入对象中
        # print("request.POST",request.POST)6f4rrty c4ty
        informantion_form = forms.PhoneInformationModelForm(request.POST)
        # 如果符合验证规则
        if informantion_form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            # informantion_form.save()
            remark = request.POST.get("remark")
            car_id = request.POST.get("car_id")
            # 未搜索到车辆号码,报错
            if not car_id:
                error_message = "请填写车号!"
                return render(request, "phone_error.html", {"error_message": error_message})
            # 同车次,同时间,同仓数,报错
            try:
                # 保存当前时间
                now = datetime.datetime.now().date()
                #############
                models.Information.objects.create(**informantion_form.cleaned_data, car_id=car_id, deliver_time=now)
            except Exception as e:
                error_message = "已填写该车该仓,请勿重复填写!"
                return render(request, "phone_error.html", {"error_message": error_message})

            # 跳转到客户列表页
            return render(request, "phone_submit.html")
        else:
            return render(request, "phone_index.html", locals())
    return render(request, "phone_index.html", locals())


@login_required
def phone_information(request):
    # 取到当前用户名
    user_obj = request.user
    # 获取今天的时间
    today = datetime.datetime.now().date()
    # 获取该车辆对象
    car_list = models.Car.objects.filter(Q(driver=user_obj) | Q(supercargo=user_obj))
    information_list = []
    for car_obj in car_list:
        # 过滤今天的数据
        information_list += models.Information.objects.filter(car=car_obj, deliver_time=today).values("car__name",
                                                                                                      "car__driver__username",
                                                                                                      "car__supercargo__username",
                                                                                                      "drive_number",
                                                                                                      "cabin",
                                                                                                      "oilwarehouse__name",
                                                                                                      "petrolstation__name",
                                                                                                      "oil__name",
                                                                                                      "paid_in_number")

    # print("information_list", list(information_list))
    return render(request, "phone_information.html", locals())


@login_required
def phone_information_audit(request):
    # 取到当前用户名
    user_obj = request.user
    # 获取今天的时间
    today = datetime.datetime.now().date()
    # 获取该员工今日已审批的数据
    staticinformation_list = models.StaticInformation.objects.filter(
        Q(driver=user_obj) | Q(supercargo=user_obj)).filter(
        deliver_time=today).values("car_name",
                                   "driver",
                                   "supercargo",
                                   "drive_number",
                                   "cabin",
                                   "oilwarehouse",
                                   "petrolstation", "oil", "paid_in_number")

    return render(request, "phone_information_audit.html", locals())


# 获取收货单位的列表
def getpetrolstation(request):
    # 获取到所选客户的ID值
    customer_id = request.GET.get("customer_id")
    # 过滤出所选客户的加油站列表
    petrolstation_list = models.Petrolstation.objects.filter(customer_id=customer_id).all()
    # 将queryset类型转化为列表类型
    res = list(petrolstation_list.values("pk", "name"))
    # 如果JsonResponse传递的不是字典类型,则需要加safe=False
    return JsonResponse(res, safe=False)


# 注册的视图函数
def register(request):
    '''
    基于ajax和modelform组件时间的注册功能
    :param request:
    :return:
    '''
    if request.method == "POST":
        # 用于记录校验的状态
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        # 利用form表单做校验(如果form表单验证通过)
        if form_obj.is_valid():
            # 删除form表中校验re_password字段
            form_obj.cleaned_data.pop("re_password")
            # 获取头像的文件,若取不到则默认avatars/default.png
            avatar_img = request.FILES.get("avatar", "avatars/default.png")
            # 校验通过,去数据库中创建一个新的用户
            models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            # 如果通过效验,就添加跳转路径
            ret["msg"] = reverse("login")
            return JsonResponse(ret)
        else:
            # 如果校验错误，就将错误保存在errors中
            # print(form_obj.errors)
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            # 如果效验失败就直接返回错误的信息
            return JsonResponse(ret)
    # 生成一个form对象
    form_obj = forms.RegForm()
    return render(request, "register.html", {"form_obj": form_obj})


# 注销视图函数
@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse("login"))


#################################用户信息################################
# 用户视图函数的CBV
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class UserinfoView(View):
    def get(self, request):
        # 查询所有的用户列表
        userinfo_list = models.UserInfo.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            q.children.append((field + "__contains", val))
            # 过滤数据
            userinfo_list = userinfo_list.filter(q)
            # customer_list=customer_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, userinfo_list.count(), request)
        # 生成每一页的初始页和结束页
        userinfo_list = userinfo_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "userinfo/userinfo_list.html",
                      {"page_num": page_num, "userinfo_list": userinfo_list, "pagination": pagination,
                       "information_notes": information_notes})

    def post(self, request):
        # 获取批量处理的方法
        func_str = request.POST.get("action")
        # 获取需要批量处理的主键值
        data = request.POST.getlist("selected_pk_list")
        # 如果option选择的是without_func
        if func_str == "without_func":
            return redirect(reverse("userinfo_list"))
        # 如果类中没有patch_delete的字符串(利用反射)
        if not hasattr(self, func_str):
            return HttpResponse("非法输入")
        else:
            queryset = models.UserInfo.objects.filter(pk__in=data)
            # 利用反射创建func方法
            func = getattr(self, func_str)
            func(request, queryset)
            # 1.跳转到当前页面
            ret = self.get(request)
            return ret

            # 2.重定向到当前的路径
            # return redirect(request.path)

    # 创建批量处理的函数
    def patch_delete(self, request, queryset):
        # 将主键值为data的所有顾客都删除
        queryset.delete()


# 添加Userinfo视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddUserinfoView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.UserinfoModelForm()
        return render(request, "add_userinfo.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.UserinfoModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            # form.save()
            # 校验通过,去数据库中创建一个新的用户
            models.UserInfo.objects.create_user(**form.cleaned_data)
            # 跳转到用户列表页
            return redirect(reverse("userinfo_list"))
        else:
            return render(request, "add_userinfo.html", {"form": form})


# 编辑用户视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditUserinfoView(View):
    def get(self, request, id):
        # 获取编辑的用户对象
        edit_obj = models.UserInfo.objects.get(pk=id)
        # 将需要编辑用户对象传入modelform表中,用户展现编辑的input框
        form = forms.UserinfoModelForm(instance=edit_obj)
        return render(request, "edit_userinfo.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /userinfo/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.UserInfo.objects.get(pk=id)

        # 必须加上instance,不然会重新创建一条记录
        form = forms.UserinfoModelForm(request.POST, instance=edit_obj)
        # print("pwd", request.POST.get("password"))
        if form.is_valid():
            edit_obj.set_password(request.POST.get("password"))
            edit_obj.save()
            # form.save()
            # 重定向到修改的那一页
            return redirect("/userinfo/list/?" + y)
        else:
            return render(request, "edit_userinfo.html", {"form": form})


# 删除用户视图函数(FBV)
@login_required
def userinfo_delete(request, userinfo_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除
    models.UserInfo.objects.filter(pk=userinfo_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("userinfo_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/userinfo/list/
    return redirect(new_path)


#################################客户信息################################
# 客户视图函数的CBV
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class CustomerView(View):
    def get(self, request):
        # 查询所有的客户列表
        customer_list = models.Customer.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            q.children.append((field + "__contains", val))
            # 过滤数据
            customer_list = customer_list.filter(q)
            # customer_list=customer_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, customer_list.count(), request)
        # 生成每一页的初始页和结束页
        customer_list = customer_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "customer/customer_list.html",
                      {"page_num": page_num, "customer_list": customer_list, "pagination": pagination,
                       "information_notes": information_notes})

    def post(self, request):
        # 获取批量处理的方法
        func_str = request.POST.get("action")
        # 获取需要批量处理的主键值
        data = request.POST.getlist("selected_pk_list")
        # 如果option选择的是without_func
        if func_str == "without_func":
            return redirect(reverse("customer_list"))
        # 如果类中没有patch_delete的字符串(利用反射)
        if not hasattr(self, func_str):
            return HttpResponse("非法输入")
        else:
            queryset = models.Customer.objects.filter(pk__in=data)
            # 利用反射创建func方法
            func = getattr(self, func_str)
            func(request, queryset)
            # 1.跳转到当前页面
            ret = self.get(request)
            return ret
            # 2.重定向到当前的路径
            # return redirect(request.path)

    # 创建批量处理的函数
    def patch_delete(self, request, queryset):
        # 将主键值为data的所有顾客都删除
        queryset.delete()


# 添加Customer视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddCustomerView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.CustomerModelForm()
        return render(request, "add_customer.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.CustomerModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到客户列表页
            return redirect(reverse("customer_list"))
        else:
            return render(request, "add_customer.html", {"form": form})


# 编辑客户视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditCustomerView(View):
    def get(self, request, id):
        # 获取编辑的客户对象
        edit_obj = models.Customer.objects.get(pk=id)
        # 将需要编辑客户对象传入modelform表中,用户展现编辑的input框
        form = forms.CustomerModelForm(instance=edit_obj)
        return render(request, "edit_customer.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /customer/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Customer.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.CustomerModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/customer/list/?" + y)
        else:
            return render(request, "edit_customer.html", {"form": form})


# 删除客户视图函数(FBV)
@login_required
def customer_delete(request, customer_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除Customer
    models.Customer.objects.filter(pk=customer_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("customer_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/customer/list/
    return redirect(new_path)


#################################车辆分类信息################################
# 车辆分类视图函数的CBV
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class CarTypeView(View):
    def get(self, request):
        # 查询所有的车辆分类列表
        car_type_list = models.CarType.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            q.children.append((field + "__contains", val))
            # 过滤数据
            car_type_list = car_type_list.filter(q)
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, car_type_list.count(), request)
        # 生成每一页的初始页和结束页
        car_type_list = car_type_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "cartype/car_type_list.html",
                      {"page_num": page_num, "car_type_list": car_type_list, "pagination": pagination,
                       "information_notes": information_notes})

    def post(self, request):
        # 获取批量处理的方法
        func_str = request.POST.get("action")
        # 获取需要批量处理的主键值
        data = request.POST.getlist("selected_pk_list")
        # 如果option选择的是without_func
        if func_str == "without_func":
            return redirect(reverse("car_type_list"))
        # 如果类中没有patch_delete的字符串(利用反射)
        if not hasattr(self, func_str):
            return HttpResponse("非法输入")
        else:
            queryset = models.CarType.objects.filter(pk__in=data)
            # 利用反射创建func方法
            func = getattr(self, func_str)
            func(request, queryset)
            # 1.跳转到当前页面
            ret = self.get(request)
            return ret
            # 2.重定向到当前的路径
            # return redirect(request.path)

    # 创建批量处理的函数
    def patch_delete(self, request, queryset):
        # 将主键值为data的所有顾客都删除
        queryset.delete()


# 添加CarType视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddCarTypeView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.CarTypeModelForm()
        return render(request, "add_car_type.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.CarTypeModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到客户列表页
            return redirect(reverse("car_type_list"))
        else:
            return render(request, "add_car_type.html", {"form": form})


# 编辑车辆分类视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditCarTypeView(View):
    def get(self, request, id):
        # 获取编辑的客户对象
        edit_obj = models.CarType.objects.get(pk=id)
        # 将需要编辑客户对象传入modelform表中,用户展现编辑的input框
        form = forms.CarTypeModelForm(instance=edit_obj)
        return render(request, "edit_car_type.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /customer/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.CarType.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.CarTypeModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/car_type/list/?" + y)
        else:
            return render(request, "edit_car_type.html", {"form": form})


# 删除车辆分类视图函数(FBV)
@login_required
def car_type_delete(request, car_type_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除Customer
    models.CarType.objects.filter(pk=car_type_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("car_type_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/customer/list/
    return redirect(new_path)


#################################12元加油站补贴################################
# 12元加油站视图函数的CBV
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class Petrolstation12View(View):
    def get(self, request):
        # 查询所有的12元加油站列表
        petrolstation12_list = models.Petrolstation12.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            q.children.append((field + "__contains", val))
            # 过滤数据
            petrolstation12_list = petrolstation12_list.filter(q)
            # customer_list=customer_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, petrolstation12_list.count(), request)
        # 生成每一页的初始页和结束页
        petrolstation12_list = petrolstation12_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "petrolstation12/petrolstation12_list.html",
                      {"page_num": page_num, "petrolstation12_list": petrolstation12_list, "pagination": pagination,
                       "information_notes": information_notes})

    def post(self, request):
        # 获取批量处理的方法
        func_str = request.POST.get("action")
        # 获取需要批量处理的主键值
        data = request.POST.getlist("selected_pk_list")
        # 如果option选择的是without_func
        if func_str == "without_func":
            return redirect(reverse("car_type_list"))
        # 如果类中没有patch_delete的字符串(利用反射)
        if not hasattr(self, func_str):
            return HttpResponse("非法输入")
        else:
            queryset = models.Petrolstation12.objects.filter(pk__in=data)
            # 利用反射创建func方法
            func = getattr(self, func_str)
            func(request, queryset)
            # 1.跳转到当前页面
            ret = self.get(request)
            return ret
            # 2.重定向到当前的路径
            # return redirect(request.path)

    # 创建批量处理的函数
    def patch_delete(self, request, queryset):
        # 将主键值为data的所有顾客都删除
        queryset.delete()


# 添加Petrolstation12视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddPetrolstation12View(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.Petrolstation12ModelForm()
        return render(request, "add_petrolstation12.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.Petrolstation12ModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到12元加油站列表页
            return redirect(reverse("petrolstation12_list"))
        else:
            return render(request, "add_petrolstation12.html", {"form": form})


# 编辑Petrolstation12视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditPetrolstation12View(View):
    def get(self, request, id):
        # 获取编辑的12元加油站
        edit_obj = models.Petrolstation12.objects.get(pk=id)
        # 将需要编辑12元加油站传入modelform表中,用户展现编辑的input框
        form = forms.Petrolstation12ModelForm(instance=edit_obj)
        return render(request, "edit_petrolstation12.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /customer/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Petrolstation12.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.Petrolstation12ModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/petrolstation12/list/?" + y)
        else:
            return render(request, "edit_petrolstation12.html", {"form": form})


# 删除12元加油站视图函数(FBV)
@login_required
def petrolstation12_delete(request, petrolstation12_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除Petrolstation12
    models.Petrolstation12.objects.filter(pk=petrolstation12_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("petrolstation12_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/customer/list/
    return redirect(new_path)


#################################30元加油站补贴################################
# 30元加油站视图函数的CBV
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class Petrolstation30View(View):
    def get(self, request):
        # 查询所有的30元加油站列表
        petrolstation30_list = models.Petrolstation30.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            q.children.append((field + "__contains", val))
            # 过滤数据
            petrolstation30_list = petrolstation30_list.filter(q)
            # customer_list=customer_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, petrolstation30_list.count(), request)
        # 生成每一页的初始页和结束页
        petrolstation30_list = petrolstation30_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "petrolstation30/petrolstation30_list.html",
                      {"page_num": page_num, "petrolstation30_list": petrolstation30_list, "pagination": pagination,
                       "information_notes": information_notes})

    def post(self, request):
        # 获取批量处理的方法
        func_str = request.POST.get("action")
        # 获取需要批量处理的主键值
        data = request.POST.getlist("selected_pk_list")
        # 如果option选择的是without_func
        if func_str == "without_func":
            return redirect(reverse("petrolstation30_list"))
        # 如果类中没有patch_delete的字符串(利用反射)
        if not hasattr(self, func_str):
            return HttpResponse("非法输入")
        else:
            queryset = models.Petrolstation30.objects.filter(pk__in=data)
            # 利用反射创建func方法
            func = getattr(self, func_str)
            func(request, queryset)
            # 1.跳转到当前页面
            ret = self.get(request)
            return ret
            # 2.重定向到当前的路径
            # return redirect(request.path)

    # 创建批量处理的函数
    def patch_delete(self, request, queryset):
        # 将主键值为data的所有顾客都删除
        queryset.delete()


# 添加Petrolstation30视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddPetrolstation30View(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.Petrolstation30ModelForm()
        return render(request, "add_petrolstation30.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.Petrolstation30ModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到30元加油站列表页
            return redirect(reverse("petrolstation30_list"))
        else:
            return render(request, "add_petrolstation30.html", {"form": form})


# 编辑Petrolstation30视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditPetrolstation30View(View):
    def get(self, request, id):
        # 获取编辑的30元加油站
        edit_obj = models.Petrolstation30.objects.get(pk=id)
        # 将需要编辑12元加油站传入modelform表中,用户展现编辑的input框
        form = forms.Petrolstation30ModelForm(instance=edit_obj)
        return render(request, "edit_petrolstation30.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /customer/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Petrolstation30.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.Petrolstation30ModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/petrolstation30/list/?" + y)
        else:
            return render(request, "edit_petrolstation30.html", {"form": form})


# 删除30元加油站视图函数(FBV)
@login_required
def petrolstation30_delete(request, petrolstation30_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除Petrolstation30
    models.Petrolstation30.objects.filter(pk=petrolstation30_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("petrolstation30_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/customer/list/
    return redirect(new_path)


#####################################车辆信息##############################
# 车辆视图函数的CBV
@method_decorator(login_required, name='get')
class CarView(View):
    def get(self, request):
        # 查询所有的车辆列表
        car_list = models.Car.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            q.children.append((field + "__contains", val))
            # 过滤数据
            car_list = car_list.filter(q)
            # car_list=car_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, car_list.count(), request)
        # 生成每一页的初始页和结束页
        car_list = car_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "car/car_list.html",
                      {"page_num": page_num, "car_list": car_list, "pagination": pagination,
                       "information_notes": information_notes})


# 删除车辆信息视图函数(FBV)
@login_required
def car_delete(request, car_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除car
    models.Car.objects.filter(pk=car_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("car_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/car/list/
    return redirect(new_path)


# 添加车辆视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddCarView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.CarModelForm()
        return render(request, "add_car.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.CarModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到客户列表页
            return redirect(reverse("car_list"))
        else:
            return render(request, "add_car.html", {"form": form})


# 编辑车辆视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditCarView(View):
    def get(self, request, id):
        # 获取编辑的车辆对象
        edit_obj = models.Car.objects.get(pk=id)
        # 将需要编辑车辆对象传入modelform表中,用户展现编辑的input框
        form = forms.CarModelForm(instance=edit_obj)
        return render(request, "edit_car.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /car/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Car.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.CarModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/car/list/?" + y)
        else:
            return render(request, "edit_car.html", {"form": form})


#################################油品###############################
# 油品视图函数的CBV
@method_decorator(login_required, name='get')
class OilView(View):
    def get(self, request):
        # 查询所有的油品列表
        oil_list = models.Oil.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            q.children.append((field + "__contains", val))
            # 过滤数据
            oil_list = oil_list.filter(q)
            # car_list=car_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, oil_list.count(), request)
        # 生成每一页的初始页和结束页
        oil_list = oil_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "oil/oil_list.html",
                      {"page_num": page_num, "oil_list": oil_list, "pagination": pagination,
                       "information_notes": information_notes})


# 删除油品信息视图函数(FBV)
@login_required
def oil_delete(request, oil_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除car
    models.Oil.objects.filter(pk=oil_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("oil_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/oil/list/
    return redirect(new_path)


# 添加油品视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddOilView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.OilModelForm()
        return render(request, "add_oil.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.OilModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到客户列表页
            return redirect(reverse("oil_list"))
        else:
            return render(request, "add_oil.html", {"form": form})


# 编辑油品视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditOilView(View):
    def get(self, request, id):
        # 获取编辑的油品对象
        edit_obj = models.Oil.objects.get(pk=id)
        # 将需要编辑油品对象传入modelform表中,用户展现编辑的input框
        form = forms.OilModelForm(instance=edit_obj)
        return render(request, "edit_oil.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /oil/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Oil.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.OilModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/oil/list/?" + y)
        else:
            return render(request, "edit_oil.html", {"form": form})


#################################油库###############################

# 油库视图函数的CBV
@method_decorator(login_required, name='get')
class OilwarehouseView(View):
    def get(self, request):
        # 查询所有的油库列表
        oilwarehouse_list = models.Oilwarehouse.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            q.children.append((field + "__contains", val))
            # 过滤数据
            oilwarehouse_list = oilwarehouse_list.filter(q)
            # car_list=car_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, oilwarehouse_list.count(), request)
        # 生成每一页的初始页和结束页
        oilwarehouse_list = oilwarehouse_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "oilwarehouse/oilwarehouse_list.html",
                      {"page_num": page_num, "oilwarehouse_list": oilwarehouse_list, "pagination": pagination,
                       "information_notes": information_notes})


# 删除油库信息视图函数(FBV)
@login_required
def oilwarehouse_delete(request, oilwarehouse_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除car
    models.Oilwarehouse.objects.filter(pk=oilwarehouse_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("oilwarehouse_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/oilwarehouse/list/
    return redirect(new_path)


# 添加油库视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddOilwarehouseView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.OilwarehouseModelForm()
        return render(request, "add_oilwarehouse.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.OilwarehouseModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到客户列表页
            return redirect(reverse("oilwarehouse_list"))
        else:
            return render(request, "add_oilwarehouse.html", {"form": form})


# 编辑油库视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditOilwarehouseView(View):
    def get(self, request, id):
        # 获取编辑油库对象
        edit_obj = models.Oilwarehouse.objects.get(pk=id)
        # 将需要编辑油库对象传入modelform表中,用户展现编辑的input框
        form = forms.OilwarehouseModelForm(instance=edit_obj)
        return render(request, "edit_oilwarehouse.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /oilwarehouse/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Oilwarehouse.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.OilwarehouseModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/oilwarehouse/list/?" + y)
        else:
            return render(request, "edit_oilwarehouse.html", {"form": form})


#################################加油站###############################

# 加油站视图函数的CBV
@method_decorator(login_required, name='get')
class PetrolstationView(View):
    def get(self, request):
        # 查询所有的加油站列表
        petrolstation_list = models.Petrolstation.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 创建Q对象，能够对字段的字符串进行过滤操作，默认and模式
            q = Q()
            # 向Q函数中添加条件
            if field == "customer":
                q.children.append((field + "__name__contains", val))
            else:
                q.children.append((field + "__contains", val))
            # 过滤数据
            petrolstation_list = petrolstation_list.filter(q)
            # car_list=car_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, petrolstation_list.count(), request)
        # 生成每一页的初始页和结束页
        petrolstation_list = petrolstation_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "petrolstation/petrolstation_list.html",
                      {"page_num": page_num, "petrolstation_list": petrolstation_list, "pagination": pagination,
                       "information_notes": information_notes})


# 删除加油站信息视图函数(FBV)
@login_required
def petrolstation_delete(request, petrolstation_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除petrolstation
    models.Petrolstation.objects.filter(pk=petrolstation_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("petrolstation_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/petrolstation/list/
    return redirect(new_path)


# 添加油库视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddPetrolstationView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.PetrolstationModelForm()
        return render(request, "add_petrolstation.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.PetrolstationModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到加油站列表页
            return redirect(reverse("petrolstation_list"))
        else:
            return render(request, "add_petrolstation.html", {"form": form})


# 编辑加油站视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditPetrolstationView(View):
    def get(self, request, id):
        # 获取编辑加油站对象
        edit_obj = models.Petrolstation.objects.get(pk=id)
        # 将需要编辑加油站对象传入modelform表中,用户展现编辑的input框
        form = forms.PetrolstationModelForm(instance=edit_obj)
        return render(request, "edit_petrolstation.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /petrolstation/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Petrolstation.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.PetrolstationModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/petrolstation/list/?" + y)
        else:
            return render(request, "edit_petrolstation.html", {"form": form})


#################################加油站油库里程###############################

# 加油站油库里程视图函数的CBV
@method_decorator(login_required, name='get')
class Petrolstation2oilwarehouseView(View):
    def get(self, request):
        # 查询所有的加油站油库里程信息列表
        petrolstation2oilwarehouse_list = models.Petrolstation2oilwarehouse.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 如果搜索的是加油站
            if field == "petrolstation":
                petrolstation_obj = models.Petrolstation.objects.filter(name__contains=val).first()
                # 过滤数据
                petrolstation2oilwarehouse_list = models.Petrolstation2oilwarehouse.objects.filter(
                    petrolstation=petrolstation_obj)


            else:
                # 如果搜索的是油库
                oilwarehouse_obj = models.Oilwarehouse.objects.filter(name__contains=val).first()
                # 过滤数据
                petrolstation2oilwarehouse_list = models.Petrolstation2oilwarehouse.objects.filter(
                    oilwarehouse=oilwarehouse_obj)

        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, petrolstation2oilwarehouse_list.count(), request)
        # 生成每一页的初始页和结束页
        petrolstation2oilwarehouse_list = petrolstation2oilwarehouse_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "petrolstation2oilwarehouse/petrolstation2oilwarehouse_list.html",
                      {"page_num": page_num, "petrolstation2oilwarehouse_list": petrolstation2oilwarehouse_list,
                       "pagination": pagination, "information_notes": information_notes})


# 删除加油站油库里程信息视图函数(FBV)
@login_required
def petrolstation2oilwarehouse_delete(request, petrolstation2oilwarehouse_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除petrolstation2oilwarehouse
    models.Petrolstation2oilwarehouse.objects.filter(pk=petrolstation2oilwarehouse_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("petrolstation2oilwarehouse_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/petrolstation2oilwarehouse/list/
    return redirect(new_path)


# 添加加油站油库里程信息视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddPetrolstation2oilwarehouseView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.Petrolstation2oilwarehouseModelForm()
        return render(request, "add_petrolstation2oilwarehouse.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.Petrolstation2oilwarehouseModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到加油站列表页
            return redirect(reverse("petrolstation2oilwarehouse_list"))
        else:
            error = ""
            # 获取选中的加油站
            petrolstation_id = request.POST.get("petrolstation")
            petrolstation_obj = models.Petrolstation.objects.filter(id=petrolstation_id).first()
            # 获取选中的油库
            oilwarehouse_id = request.POST.get("oilwarehouse")
            oilwarehouse_obj = models.Oilwarehouse.objects.filter(id=oilwarehouse_id).first()
            petrolstation2oilwarehouse_obj = models.Petrolstation2oilwarehouse.objects.filter(
                oilwarehouse=oilwarehouse_obj,
                petrolstation=petrolstation_obj).first()
            # 如果已经存在相同的油库和加油站
            if petrolstation2oilwarehouse_obj:
                error = "已有该油库和加油站的数据,请勿重新填写!"
            return render(request, "add_petrolstation2oilwarehouse.html", {"form": form, "error": error})


# 编辑加油站油库里程视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditPetrolstation2oilwarehouseView(View):
    def get(self, request, id):
        # 获取编辑加油站油库里程对象
        edit_obj = models.Petrolstation2oilwarehouse.objects.get(pk=id)
        # 将需要编辑加油站对象传入modelform表中,用户展现编辑的input框
        form = forms.Petrolstation2oilwarehouseModelForm(instance=edit_obj)
        return render(request, "edit_petrolstation2oilwarehouse.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /petrolstation2oilwarehouse/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Petrolstation2oilwarehouse.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.Petrolstation2oilwarehouseModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/petrolstation2oilwarehouse/list/?" + y)
        else:
            return render(request, "edit_petrolstation2oilwarehouse.html", {"form": form})


#################################客户里程价格###############################

# 客户里程价格视图函数的CBV
@method_decorator(login_required, name='get')
class Customer2mileageView(View):
    def get(self, request):
        # 查询所有的客户里程价格信息列表
        customer2mileage_list = models.Customer2Mileage.objects.all()
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            customer_obj = models.Customer.objects.filter(name__contains=val).first()
            # 过滤数据
            customer2mileage_list = customer2mileage_list.filter(customer=customer_obj)
            # car_list=car_list.filter(Q(name__contains=val)|Q(qq__contains=val))
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, customer2mileage_list.count(), request)
        # 生成每一页的初始页和结束页
        customer2mileage_list = customer2mileage_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "customer2mileage/customer2mileage_list.html",
                      {"page_num": page_num, "customer2mileage_list": customer2mileage_list, "pagination": pagination,
                       "information_notes": information_notes})


# 删除客户里程价格信息视图函数(FBV)
@login_required
def customer2mileage_delete(request, customer2mileage_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")

    # 删除customer2mileage
    models.Customer2Mileage.objects.filter(pk=customer2mileage_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("customer2mileage_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/customer2mileage/list/
    return redirect(new_path)


# 添加客户里程价格信息视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AddCustomer2mileageView(View):
    def get(self, request):
        # 获取modelform对象
        form = forms.Customer2mileageModelForm()
        return render(request, "add_customer2mileage.html", {"form": form})

    def post(self, request):
        # 创建ModelForm对象,并将request.POST传入对象中
        form = forms.Customer2mileageModelForm(request.POST)
        # 如果符合验证规则
        if form.is_valid():
            # 效验成功就保存下(将数据保存在数据库中)
            form.save()
            # 跳转到加油站列表页
            return redirect(reverse("customer2mileage_list"))
        else:
            return render(request, "add_customer2mileage.html", {"form": form})


# 编辑客户里程价格视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditCustomer2mileageView(View):
    def get(self, request, id):
        # 获取编辑客户里程价格对象
        edit_obj = models.Customer2Mileage.objects.get(pk=id)
        # 将需要编辑客户里程价格对象传入modelform表中,用户展现编辑的input框
        form = forms.Customer2mileageModelForm(instance=edit_obj)
        return render(request, "edit_customer2mileage.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /customer2mileage/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Customer2Mileage.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.Customer2mileageModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            # 重定向到修改的那一页
            return redirect("/customer2mileage/list/?" + y)
        else:
            return render(request, "edit_customer2mileage.html", {"form": form})


#################################信息管理列表###############################

# 信息列表管理视图函数的CBV
@method_decorator(login_required, name='get')
class InformationView(View):
    def get(self, request):
        # 查询所有的信息管理列表
        information_list = models.Information.objects.all().order_by("-deliver_time", "car", "drive_number", "cabin")
        # 通过GET请求获取搜索的内容
        val = request.GET.get("q")
        # 通过GET请求获取搜索的条件
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 如果搜索条件是车号
            if field == "car_name":
                # 创建Q对象,对字符进行过滤操作,默认and模式
                q = Q()
                # 向Q函数中添加过滤条件
                q.children.append(("name" + "__contains", val))
                # 获取过滤后的car对象
                car_obj = models.Car.objects.filter(q).first()
                information_list = models.Information.objects.filter(car=car_obj).order_by("-deliver_time", "car",
                                                                                           "drive_number", "cabin")
            # 如果搜索条件是配送时间
            elif field == "deliver_time":
                try:
                    # 如果是单个时间
                    if val.find(":") == -1:
                        # 创建Q对象,过滤(默认and模式)
                        q = Q()
                        # 向q对象中添加过滤条件
                        q.children.append(("deliver_time", val))
                        # 获取过滤后的数据
                        information_list = models.Information.objects.filter(q).order_by("-deliver_time", "car",
                                                                                         "drive_number", "cabin")
                    # 如果是时间段
                    else:
                        start_time_str, end_time_str = val.split(":")
                        start_time_str = start_time_str.strip()
                        end_time_str = end_time_str.strip()
                        # 获取过滤后的数据
                        information_list = models.Information.objects.filter(
                            deliver_time__range=(start_time_str, end_time_str)).order_by("-deliver_time", "car",
                                                                                         "drive_number", "cabin")

                except Exception:
                    return HttpResponse("必须为合法的日期格式，请使用 YYYY-MM-DD 格式。")
            # 如果搜索条件是外部编号
            elif field == "outside_number":
                # 创建Q对象,过滤(默认and模式)
                q = Q()
                # 向q对象中添加过滤条件
                q.children.append(("outside_number" + "__contains", val))
                # 获取过滤后的数据
                information_list = models.Information.objects.filter(q).order_by("-deliver_time", "car", "drive_number",
                                                                                 "cabin")
            # 如果搜索条件是内部编号
            elif field == "inside_number":
                # 创建Q对象,过滤(默认and模式)
                q = Q()
                # 向q对象中添加过滤条件
                q.children.append(("inside_number" + "__contains", val))
                # 获取过滤后的数据
                information_list = models.Information.objects.filter(q).order_by("-deliver_time", "car", "drive_number",
                                                                                 "cabin")
            # 如果搜索条件是驾驶员
            elif field == "driver_name":
                # 获取人员对象
                user_obj = models.UserInfo.objects.filter(username=val).first()
                car_obj = models.Car.objects.filter(driver=user_obj).first()
                # 获取过滤后的数据
                information_list = models.Information.objects.filter(car=car_obj).order_by("-deliver_time", "car",
                                                                                           "drive_number", "cabin")
            # 如果搜索条件是押运员
            elif field == "supercargo_name":
                # 获取人员对象
                user_obj = models.UserInfo.objects.filter(username=val).first()
                car_obj = models.Car.objects.filter(supercargo=user_obj).first()
                # 获取过滤后的数据
                information_list = models.Information.objects.filter(car=car_obj).order_by("-deliver_time", "car",
                                                                                           "drive_number", "cabin")
            # 如果搜索条件是发货单位
            elif field == "customer_name":
                # 获取人员对象
                customer_obj = models.Customer.objects.filter(name=val).first()

                # 获取过滤后的数据
                information_list = models.Information.objects.filter(customer=customer_obj).order_by("-deliver_time",
                                                                                                     "car",
                                                                                                     "drive_number",
                                                                                                     "cabin")
            # 如果搜索条件是审核状态
            elif field == "audit_status":
                dic = {"未审核": 1, "已审核": 2}
                int_audit_status = dic.get(val.strip(), 1)
                # 获取过滤后的数据
                information_list = models.Information.objects.filter(status_audit=int_audit_status).order_by(
                    "-deliver_time",
                    "car",
                    "drive_number",
                    "cabin")
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, information_list.count(), request)
        # 生成每一页的初始页和结束页
        information_list = information_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 传递Url参数,使其能够导出数据
        q = request.GET.get("q")
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "information_list.html",
                      {"page_num": page_num, "information_list": information_list, "pagination": pagination,
                       "information_notes": information_notes, "field": field, "q": q})


# 删除填写信息视图函数(FBV)
@login_required
def information_delete(request, information_delete_id):
    # 获取Page页码
    page_num = request.GET.get("page")
    # 删除customer2mileage
    models.Information.objects.filter(pk=information_delete_id).delete()
    # 拼接跳转url
    re_url = reverse("information_list")
    new_path = re_url + "?page=" + page_num
    # 跳转到/information/list/
    return redirect(new_path)


# 编辑填写信息视图函数(CBV)
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class EditInformationView(View):
    def get(self, request, id):
        # 获取编辑客户里程价格对象
        edit_obj = models.Information.objects.get(pk=id)
        # 将需要编辑客户里程价格对象传入modelform表中,用户展现编辑的input框
        form = forms.InformationModelForm(instance=edit_obj)
        return render(request, "edit_information.html", {"form": form})

    def post(self, request, id):
        # 获取URL
        full_path = request.get_full_path()  # /customer2mileage/edit/12?page=1
        # 获取page=2
        x, y = full_path.split("?")
        edit_obj = models.Information.objects.get(pk=id)
        # 必须加上instance,不然会重新创建一条记录
        form = forms.InformationModelForm(request.POST, instance=edit_obj)
        try:
            if form.is_valid():
                form.save()
                # 重定向到修改的那一页
                return redirect("/information/list/?" + y)
            else:
                return render(request, "edit_information.html", {"form": form})
        except Exception as e:
            return HttpResponse("修改错误!")


# 统计客户成单数类
class OrderstatisticsView(View):
    # 获取今天的列表函数
    def today(self, request):
        # 获取今天的时间
        today = datetime.datetime.now().date()
        # 过滤今天的数据
        staticinformation_list = models.StaticInformation.objects.filter(deliver_time=today)

        # 查询每一个客户以及对应的今天的成单量
        obj_list = models.StaticInformation.objects.filter(deliver_time=today).values("customer_name").annotate(
            c=Count(1)).values_list("customer_name", "c")

        customer_list = models.Customer.objects.all()
        new_list = []
        for i in customer_list:
            new_list.append(i.name)
        new_obj_list = []
        for i in list(obj_list):
            new_obj_list.append(i[0])
        c = []
        for i in new_list:
            if i not in new_obj_list:
                c.append(i)
        d = []
        for i in c:
            d.append((i, 0))
        for i in list(obj_list):
            d.append(i)
        # 将queryset转换成list类型,并且转换成列表套列表的形式
        ret = [[item[0], item[1]] for item in d]
        content = "今天的成单量"
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        ############## 分页
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, staticinformation_list.count(), request)
        # 生成每一页的初始页和结束页
        staticinformation_list = staticinformation_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        return {"pagination": pagination, "page_num": page_num, "ret": ret, "today": today, "content": content,
                "information_notes": information_notes, "staticinformation_list": staticinformation_list}

    # 获取昨天的列表函数
    def yesterday(self, request):
        # 获取昨天的时间
        today = datetime.datetime.now().date()
        # 获取昨天的日期
        yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
        # 过滤昨天的数据
        staticinformation_list = models.StaticInformation.objects.filter(deliver_time=yesterday)
        # 查询每一个客户以及对应的昨天的成单量
        obj_list = models.StaticInformation.objects.filter(deliver_time=yesterday).values(
            "customer_name").annotate(
            c=Count(1)).values_list("customer_name", "c")

        customer_list = models.Customer.objects.all()
        new_list = []
        for i in customer_list:
            new_list.append(i.name)
        new_obj_list = []
        for i in list(obj_list):
            new_obj_list.append(i[0])
        c = []
        for i in new_list:
            if i not in new_obj_list:
                c.append(i)
        d = []
        for i in c:
            d.append((i, 0))
        for i in list(obj_list):
            d.append(i)
        # 将queryset转换成list类型,并且转换成列表套列表的形式
        ret = [[item[0], item[1]] for item in d]
        content = "昨天的成单量"
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        ############## 分页
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, staticinformation_list.count(), request)
        # 生成每一页的初始页和结束页
        staticinformation_list = staticinformation_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        return {"pagination": pagination, "page_num": page_num, "staticinformation_list": staticinformation_list,
                "ret": ret, "today": today, "content": content,
                "information_notes": information_notes}

    # 获取最近一周的列表函数
    def week(self, request):
        # 获取一周前的日期
        weekdelta = datetime.datetime.now().date() - datetime.timedelta(weeks=1)
        # 获取今天的日期
        today = datetime.datetime.now().date()
        # 过滤最近一周的数据
        staticinformation_list = models.StaticInformation.objects.filter(deliver_time__gte=weekdelta,
                                                                         deliver_time__lte=today)
        # 查询每一个客户以及对应的最近一周的成单量
        obj_list = models.StaticInformation.objects.filter(deliver_time__gte=weekdelta,
                                                           deliver_time__lte=today).values("customer_name").annotate(
            c=Count(1)).values_list("customer_name", "c")
        customer_list = models.Customer.objects.all()
        new_list = []
        for i in customer_list:
            new_list.append(i.name)
        new_obj_list = []
        for i in list(obj_list):
            new_obj_list.append(i[0])
        c = []
        for i in new_list:
            if i not in new_obj_list:
                c.append(i)
        d = []
        for i in c:
            d.append((i, 0))
        for i in list(obj_list):
            d.append(i)
        # 将queryset转换成list类型,并且转换成列表套列表的形式
        ret = [[item[0], item[1]] for item in d]
        content = "最近一周的成单量"
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        ############## 分页
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, staticinformation_list.count(), request)
        # 生成每一页的初始页和结束页
        staticinformation_list = staticinformation_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        return {"pagination": pagination, "page_num": page_num, "staticinformation_list": staticinformation_list,
                "ret": ret, "today": today, "content": content,
                "information_notes": information_notes}

    # 获取最近一月的列表函数
    def month(self, request):
        # 获取一月前的日期
        monthdelta = datetime.datetime.now().date() - datetime.timedelta(weeks=4)
        # 获取今天的日期
        today = datetime.datetime.now().date()
        # 过滤最近一月的数据
        staticinformation_list = models.StaticInformation.objects.filter(deliver_time__gte=monthdelta,
                                                                         deliver_time__lte=today)
        # 查询每一个客户以及对应的最近一个月的成单量
        obj_list = models.StaticInformation.objects.filter(deliver_time__gte=monthdelta,
                                                           deliver_time__lte=today).values("customer_name").annotate(
            c=Count(1)).values_list("customer_name", "c")
        customer_list = models.Customer.objects.all()
        new_list = []
        for i in customer_list:
            new_list.append(i.name)
        new_obj_list = []
        for i in list(obj_list):
            new_obj_list.append(i[0])
        c = []
        for i in new_list:
            if i not in new_obj_list:
                c.append(i)
        d = []
        for i in c:
            d.append((i, 0))
        for i in list(obj_list):
            d.append(i)
        # 将queryset转换成list类型,并且转换成列表套列表的形式
        ret = [[item[0], item[1]] for item in d]
        content = "最近一个月的成单量"
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        ############## 分页
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, staticinformation_list.count(), request)
        # 生成每一页的初始页和结束页
        staticinformation_list = staticinformation_list[pagination.start:pagination.end]
        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        return {"pagination": pagination, "page_num": page_num, "staticinformation_list": staticinformation_list,
                "ret": ret, "today": today, "content": content,
                "information_notes": information_notes}

    def get(self, request):
        # 获取date参数,若取不到则取今天
        date = request.GET.get("date", "today")
        context = {}
        # 反射
        if hasattr(self, date):
            context = getattr(self, date)(request)
        return render(request, "information/orderstatistics.html", context)


# 工资结算+审批函数
def information_audit(request, information_audit_id):
    # 获取Page页码
    page_num = request.GET.get("page", 1)
    # 获取搜索字段名称
    field = request.GET.get("field", "")
    # 获取搜索的内容
    q = request.GET.get("q", "")
    # 获取想要审批的那条信息
    information_query = models.Information.objects.filter(pk=information_audit_id)
    # 如果是未审核状态
    if information_query.first().status_audit != 2:
        # 拼接跳转url
        re_url = reverse("information_list")
        new_path = re_url + "?page=" + page_num + "&field=" + field + "&q=" + q
        # 计算短程价格
        # 获取information审核对象
        information_obj = models.Information.objects.filter(pk=information_audit_id).first()
        # 获取到当前审批的油库
        oilwarehouse = information_obj.oilwarehouse
        # 获取到当前审批的加油站
        petrolstation = information_obj.petrolstation
        # 获取到对应的加油站油库里程对象
        petrolstation2oilwarehouse_obj = models.Petrolstation2oilwarehouse.objects.filter(oilwarehouse=oilwarehouse,
                                                                                          petrolstation=petrolstation).first()
        try:
            shortmileage_price = information_obj.customer.customer_mileage.shortmileage_price
        except Exception as e:
            return HttpResponse("请维护对应的客户里程信息!")
        # 若没有对应的客户里程,则报错
        try:
            # 获取客户里程数
            customer_mileage = petrolstation2oilwarehouse_obj.customer_mileage
            # 获取员工里程数
            mileage = petrolstation2oilwarehouse_obj.mileage
            # print("mileage", customer_mileage)
        except AttributeError:
            no_mileage = "没有对应的客户里程,请在基础数据中进行维护!"
            return render(request, 'information/information_list.html', {"no_mileage": no_mileage})

        # 异常处理找不到短程标准
        try:
            # 获取inforamtion对应的客户短程标准
            shortmileage_standard = information_obj.customer.customer_mileage.shortmileage_standard
            # print("shortmileage_standard", shortmileage_standard)
        except Exception as e:
            no_shortmileage_standard = "没有对应的短途标准,请在基础数据中进行维护!"
            return render(request, 'information/information_list.html',
                          {"no_shortmileage_standard": no_shortmileage_standard})
        # 异常处理找不到长途单价
        try:
            # 获取inforamtion对应的客户长途的单价
            longmileage_price = information_obj.customer.customer_mileage.longmileage_price
            # print("longmileage_price", longmileage_price)
        except Exception as e:
            return HttpResponse("没有对应的长途单价,请在基础数据中进行维护!")
        # 将里程数和客户短程标准作比较
        if customer_mileage <= shortmileage_standard:
            # 如果里程数小于短程标准,则计算短程的运费
            information_obj.short_price = Decimal(information_obj.paid_in_number) * Decimal(
                shortmileage_price)
            # 长途的运费则为0
            information_obj.long_price = 0
            # 设置审核人为当前登录人
            information_obj.auditor = request.user.username
            # 改变审批状态
            information_obj.status_audit = 2
            information_obj.save()
        else:
            # 如果里程大于短途标准,则计算长途的运费
            information_obj.long_price = Decimal(customer_mileage) * Decimal(
                information_obj.paid_in_number) * Decimal(longmileage_price)
            information_obj.short_price = 0
            # 设置审核人为当前登录人
            information_obj.auditor = request.user.username
            # 改变审批状态
            information_obj.status_audit = 2
            information_obj.save()

        # 创建静态表数据
        models.StaticInformation.objects.create(
            inside_number=information_obj.inside_number,
            outside_number=information_obj.outside_number,
            customer_name=information_obj.customer.name,
            deliver_time=information_obj.deliver_time,
            car_name=information_obj.car.name,
            driver=information_obj.car.driver,
            supercargo=information_obj.car.supercargo,
            oilwarehouse=information_obj.oilwarehouse.name,
            petrolstation=information_obj.petrolstation.name,
            oil=information_obj.oil.name,
            drive_number=information_obj.drive_number,
            cabin=information_obj.cabin,
            price=information_obj.price,
            paid_in_number=information_obj.paid_in_number,
            # 员工运距
            mileage=mileage,
            # 客户运距
            customer_mileage=customer_mileage,
            shortmileage_standard=shortmileage_standard,
            shortmileage_price=shortmileage_price,
            longmileage_price=longmileage_price,
            short_price=information_obj.short_price,
            long_price=information_obj.long_price,
            car_type=information_obj.car.car_type,
            oiltank_number=information_obj.oiltank_number,
            remark=information_obj.remark
        )
        # 跳转到/information/list/?page=2
        return redirect(new_path)
    else:
        return render(request, "audit_faild.html")


#################################统计运费列表###############################
# 统计运费视图函数的CBV
@method_decorator(login_required, name='get')
class SettlementView(View):
    def get(self, request):
        # 查询所有的统计运费管理列表
        staticinformation_list = models.StaticInformation.objects.all().order_by("-deliver_time", "car_name",
                                                                                 "drive_number", "cabin")
        # 通过GET请求获取q
        val = request.GET.get("q")
        # 通过GET请求获取field
        field = request.GET.get("field")
        # 如果能够获取到q的过滤条件
        if val:
            # 如果搜索条件是车号
            if field == "car_name":
                staticinformation_list = models.StaticInformation.objects.filter(car_name=val).order_by("-deliver_time",
                                                                                                        "car_name",
                                                                                                        "drive_number",
                                                                                                        "cabin")
            # 如果搜索条件是配送时间
            elif field == "deliver_time":
                try:
                    # 如果是单个时间
                    if val.find(":") == -1:
                        # 创建Q对象,过滤(默认and模式)
                        q = Q()
                        # 向q对象中添加过滤条件
                        q.children.append(("deliver_time", val))
                        # 获取过滤后的数据
                        staticinformation_list = models.StaticInformation.objects.filter(q).order_by("-deliver_time",
                                                                                                     "car_name",
                                                                                                     "drive_number",
                                                                                                     "cabin")
                    # 时间段
                    else:
                        start_time_str, end_time_str = val.split(":")
                        start_time_str = start_time_str.strip()
                        end_time_str = end_time_str.strip()

                        # 获取过滤后的数据
                        staticinformation_list = models.StaticInformation.objects.filter(
                            deliver_time__range=(start_time_str, end_time_str)).order_by("-deliver_time",
                                                                                         "car_name",
                                                                                         "drive_number",
                                                                                         "cabin")


                except Exception:
                    return HttpResponse("必须为合法的日期格式，请使用 YYYY-MM-DD 格式。")
            # 如果搜索条件是外部编号
            elif field == "outside_number":
                # 获取过滤后的数据
                staticinformation_list = models.StaticInformation.objects.filter(outside_number__contains=val).order_by(
                    "-deliver_time", "car_name", "drive_number", "cabin")
            # 如果搜索条件是内部编号
            elif field == "inside_number":
                # 获取过滤后的数据
                staticinformation_list = models.StaticInformation.objects.filter(inside_number__contains=val).order_by(
                    "-deliver_time", "car_name", "drive_number", "cabin")
            # 如果搜索条件是驾驶员
            elif field == "driver_name":
                # 获取过滤后的数据
                staticinformation_list = models.StaticInformation.objects.filter(driver=val).order_by("-deliver_time",
                                                                                                      "car_name",
                                                                                                      "drive_number",
                                                                                                      "cabin")
            # 如果搜索条件是押运员
            elif field == "supercargo_name":
                # 获取过滤后的数据
                staticinformation_list = models.StaticInformation.objects.filter(supercargo=val).order_by(
                    "-deliver_time", "car_name", "drive_number", "cabin")
            # 如果搜索条件是发货单位
            elif field == "customer_name":
                # 获取过滤后的数据
                staticinformation_list = models.StaticInformation.objects.filter(customer_name=val).order_by(
                    "-deliver_time", "car_name", "drive_number", "cabin")
        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, staticinformation_list.count(), request)
        # 生成每一页的初始页和结束页
        staticinformation_list = staticinformation_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        # 通过GET请求获取q
        q = request.GET.get("q")
        return render(request, "settlement/settlement_list.html",
                      {"page_num": page_num, "staticinformation_list": staticinformation_list, "pagination": pagination,
                       "information_notes": information_notes, "field": field, "q": q})


#################################工资列表###############################
# 工资不去重视图函数的CBV
@method_decorator(login_required, name='get')
class EarningView(View):
    def get(self, request):
        # 获取搜索条件
        field = request.GET.get("field")
        # 获取搜索内容
        q = request.GET.get("q")

        # 执行原生的sql语句,获取全部的不去重数据
        staticinformation_list = models.StaticInformation.objects.raw(
            "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
        )
        # 如果有搜索内容
        if q:
            # 如果搜索条件是配送时间
            if field == "deliver_time":
                # 如果在q中存在:(也就是说是两个时间之间)
                if q.find(":") != -1:
                    # 开始时间和结束时间分割
                    start_time_str, end_time_str = q.split(":")
                    start_time_str = start_time_str.strip()
                    end_time_str = end_time_str.strip()
                    # 执行原生的sql语句,获取全部的不去重数据
                    # 执行两个时间之间的查询
                    staticinformation_list = models.StaticInformation.objects.raw(
                        "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where deliver_time between %s and %s group by driver,deliver_time,drive_number order by deliver_time desc",
                        [start_time_str, end_time_str]
                    )
                else:
                    # 执行原生的sql语句,获取全部的不去重数据
                    staticinformation_list = models.StaticInformation.objects.raw(
                        "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where deliver_time=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                        [q]
                    )
            # 如果搜索条件是车号
            elif field == "car_name":
                # 执行原生的sql语句,获取全部的不去重数据
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where car_name=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [q]
                )
            # 如果搜索条件是驾驶员
            elif field == "driver":
                # 执行原生的sql语句,获取全部的不去重数据
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where driver=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [q]
                )
            # 如果搜索条件是车号
            elif field == "supercargo":
                # 执行原生的sql语句,获取全部的不去重数据
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where supercargo=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [q]
                )
        else:
            # 执行原生的sql语句,获取全部的不去重数据
            staticinformation_list = models.StaticInformation.objects.raw(
                "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
            )

        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, len(staticinformation_list), request)
        # 生成每一页的初始页和结束页
        staticinformation_list = staticinformation_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()
        return render(request, "earning/earning_list.html",
                      {"page_num": page_num, "staticinformation_list": staticinformation_list,
                       "pagination": pagination,
                       "information_notes": information_notes})


# 工资去重视图函数的CBV
@method_decorator(login_required, name='get')
class EarningDistinctView(View):
    def get(self, request):
        # 获取搜索条件
        field = request.GET.get("field")
        # 获取搜索内容
        q = request.GET.get("q")

        # 执行原生的sql语句
        staticinformation_list = models.StaticInformation.objects.raw(
            "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
        )

        # 如果有搜索内容
        if q:
            # 如果搜索条件是配送时间
            if field == "deliver_time":
                # 如果在q中存在:(也就是说是两个时间之间)
                if q.find(":") != -1:
                    # 开始时间和结束时间分割
                    start_time_str, end_time_str = q.split(":")
                    start_time_str = start_time_str.strip()
                    end_time_str = end_time_str.strip()
                    # 执行原生的sql语句,获取全部的不去重数据
                    # 执行两个时间之间的查询
                    # 执行原生的sql语句
                    staticinformation_list = models.StaticInformation.objects.raw(
                        "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where deliver_time between %s and %s group by driver,deliver_time,drive_number order by deliver_time desc",
                        [start_time_str, end_time_str]
                    )
                else:
                    # 执行原生的sql语句
                    staticinformation_list = models.StaticInformation.objects.raw(
                        "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where deliver_time=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                        [q]
                    )

            # 如果搜索条件是车号
            elif field == "car_name":
                # 执行原生的sql语句
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where car_name=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [q]
                )
            # 如果搜索条件是驾驶员
            elif field == "driver":
                # 执行原生的sql语句
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where driver=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [q]
                )
            # 如果搜索条件是押运员
            elif field == "supercargo":
                # 执行原生的sql语句
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where supercargo=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [q]
                )

        # 遍历sql语句
        for distinct_information in staticinformation_list:
            # 分隔去重后的加油站
            distinct_petrolstation_list = distinct_information.petrolstation.split("/")
            # 分隔去重后的油库
            distinct_oilwarehouse_list = distinct_information.oilwarehouse.split("/")
            # 分隔去重后的里程(求出最大的里程数)
            mileage_list = distinct_information.mileage.split("/")
            mileage_list = [int(x) for x in mileage_list]
            distinct_information.max_mileage = max(mileage_list)
            # 计算分割后的加油站个数
            petrolstation_count = len(distinct_petrolstation_list) - 1
            # 计算分割后的油库个数
            oilwarehouse_count = len(distinct_oilwarehouse_list) - 1
            # 计算分割后的加油站油库/个数
            distinct_information.oilwarehouse_petrolstation_count = petrolstation_count + oilwarehouse_count
            #######(工资等于去重后的加油站个数-1)*12
            distinct_information.earning += (petrolstation_count + oilwarehouse_count) * 12
            # 获取一车的油罐数
            oiltank_number_list = distinct_information.oiltank_number.split("/")
            # print("oiltank_number_list", oiltank_number_list)
            for oiltank_number in oiltank_number_list:
                distinct_information.earning += int(oiltank_number) * 2
            #########################按车型的工资
            # # 如果车型是17-18吨的车
            # if distinct_information.car_type == "17-18吨的车":
            #     # 获取里程列表
            #     mileage_list = distinct_information.mileage.split("/")
            #     # 将列表中的字符串都转化成int类型,便于作比较
            #     mileage_list = [int(x) for x in mileage_list]
            #     # 如果一车中最大的里程小于36公里,就是50
            #     if max(mileage_list) < 36:
            #         distinct_information.earning += 50
            #     # 否则里程*0.6+29
            #     else:
            #         distinct_information.earning += Decimal(29 + max(mileage_list) * 0.6).quantize(
            #             Decimal('0.00'))
            # 如果车型是 20吨的车
            if distinct_information.car_type == "20吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 将列表中的字符串都转化成int类型,便于作比较
                mileage_list = [int(x) for x in mileage_list]
                # 如果一车中最大的里程小于36公里,就是50
                if max(mileage_list) < 36:
                    distinct_information.earning += 50
                # 否则里程*0.6+29
                else:
                    distinct_information.earning += Decimal(29 + max(mileage_list) * 0.6).quantize(
                        Decimal('0.00'))
            # 如果车型是 30吨的车
            elif distinct_information.car_type == "30吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 将列表中的字符串都转化成int类型,便于作比较
                mileage_list = [int(x) for x in mileage_list]
                # 如果一车中最大的里程小于36公里,就是60
                if max(mileage_list) < 36:
                    distinct_information.earning += 60
                # 否则里程*0.9+39
                else:
                    distinct_information.earning += Decimal(39 + max(mileage_list) * 0.9).quantize(
                        Decimal('0.00'))
            # 如果车型是 33吨的车
            elif distinct_information.car_type == "33吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 将列表中的字符串都转化成int类型,便于作比较
                mileage_list = [int(x) for x in mileage_list]
                # 如果一车中最大的里程小于36公里,就是63
                if max(mileage_list) < 36:
                    distinct_information.earning += 63
                # 否则里程*0.95+42
                else:
                    distinct_information.earning += Decimal(42 + max(mileage_list) * 0.95).quantize(
                        Decimal('0.00'))

            # 获取所有12元加油站对象######################12元加油站
            petrolstation12_list = models.Petrolstation12.objects.all()
            # 获取所有12元加油站的名称集合
            petrolstation12_name_list = []
            for petrolstation12 in petrolstation12_list:
                petrolstation12_name_list.append(petrolstation12.name)
            # print(petrolstation12_name_list)
            # 获取所有30元加油站对象######################30元加油站
            petrolstation30_list = models.Petrolstation30.objects.all()
            # 获取所有30元加油站的名称集合
            petrolstation30_name_list = []
            for petrolstation30 in petrolstation30_list:
                petrolstation30_name_list.append(petrolstation30.name)

            # 获取当前的去重加油站
            petrolstation_list = distinct_information.petrolstation.split("/")
            # 求两个列表的交集
            list3 = list(set(petrolstation12_name_list).intersection(set(petrolstation_list)))
            list4 = list(set(petrolstation30_name_list).intersection(set(petrolstation_list)))
            # 如果有交集：
            # 如果即在12元又有30元，就只加30
            if list4 and list3:
                distinct_information.earning += 30
            # 如果只有12元，就只加12元
            elif list3:
                distinct_information.earning += 12
            # 如果只有30元，就只加30元
            elif list4:
                distinct_information.earning += 30
            ###########加油站1为: 大唐/仙鹤/吕港   加油站2为:  城北/南苑/粮运/北新/东郊/
            ##############如果加油站1 和加油站站2中都有一个,工资就加30
            list5 = ["大唐", "鹤洋", "吕港"]
            list6 = ["城北", "南苑", "粮运", "北新", "东郊"]
            new_list5 = list(set(list5).intersection(set(petrolstation_list)))
            new_list6 = list(set(list6).intersection(set(petrolstation_list)))
            if new_list5 and new_list6:
                distinct_information.earning += 30

        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, len(staticinformation_list), request)
        # 生成每一页的初始页和结束页
        staticinformation_list = staticinformation_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()

        q = request.GET.get("q")
        field = request.GET.get("field")
        return render(request, "earning/earning_list_distinct.html",
                      {"page_num": page_num, "staticinformation_list": staticinformation_list,
                       "pagination": pagination,
                       "information_notes": information_notes, "q": q, "field": field})


###############导出信息列表excel#####################
# 导出信息
def export_imformation(request):
    # 获取搜索字段
    field = request.GET.get("field")
    # 获取搜索条件
    q = request.GET.get("q")
    # 获取全部运费信息
    information_list = models.Information.objects.all().order_by("-deliver_time", "car", "drive_number", "cabin")
    # 如果q有值
    if q:
        # 如果获取的是配送时间
        if field == "deliver_time":
            # 如果是单个时间
            if q.find(":") == -1:
                information_list = models.Information.objects.filter(deliver_time=q).order_by("-deliver_time", "car",
                                                                                              "drive_number", "cabin")
            # 如果获取的是时间段
            else:
                start_time_str, end_time_str = q.split(":")
                start_time_str = start_time_str.strip()
                end_time_str = end_time_str.strip()
                information_list = models.Information.objects.filter(
                    deliver_time__range=(start_time_str, end_time_str)).order_by("-deliver_time", "car",
                                                                                 "drive_number", "cabin")

        # 如果获取的是车号
        elif field == "car_name":
            information_list = models.Information.objects.filter(car__name=q).order_by("-deliver_time", "car",
                                                                                       "drive_number", "cabin")
        # 如果获取的是外部单号
        elif field == "outside_number":
            information_list = models.Information.objects.filter(outside_number=q).order_by("-deliver_time", "car",
                                                                                            "drive_number", "cabin")
        # 如果获取的是内部单号
        elif field == "inside_number":
            information_list = models.Information.objects.filter(inside_number=q).order_by("-deliver_time", "car",
                                                                                           "drive_number", "cabin")
        # 如果获取的是驾驶员
        elif field == "driver_name":
            information_list = models.Information.objects.filter(car__diver__username=q).order_by("-deliver_time",
                                                                                                  "car", "drive_number",
                                                                                                  "cabin")
        # 如果获取的是押运员
        elif field == "supercargo_name":
            information_list = models.Information.objects.filter(car__supercargo__username=q).order_by("-deliver_time",
                                                                                                       "car",
                                                                                                       "drive_number",
                                                                                                       "cabin")
        # 如果获取的是发货单位
        elif field == "customer_name":
            information_list = models.Information.objects.filter(customer__name=q).order_by("-deliver_time",
                                                                                            "car",
                                                                                            "drive_number",
                                                                                            "cabin")
        # 如果获取的是审核状态
        elif field == "audit_status":
            dic = {"未审核": 1, "已审核": 2}
            int_audit_status = dic.get(q.strip(), 1)
            information_list = models.Information.objects.filter(status_audit=int_audit_status).order_by(
                "-deliver_time",
                "car",
                "drive_number",
                "cabin")
    else:
        # 如果没有获取到q,则导出全部数据
        information_list = models.Information.objects.all().order_by("-deliver_time", "car", "drive_number", "cabin")

    # 日期格式
    datastyle = xlwt.XFStyle()
    datastyle.num_format_str = 'yyyy-mm-dd'
    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    sheet.col(5).width = 256 * 15
    sheet.col(6).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '内部编号', style_heading)
    sheet.write(0, 2, '外部编号', style_heading)
    sheet.write(0, 3, '发货单位', style_heading)
    sheet.write(0, 4, '配送时间', style_heading)
    sheet.write(0, 5, '车号', style_heading)
    sheet.write(0, 6, '驾驶员', style_heading)
    sheet.write(0, 7, '押运员', style_heading)
    sheet.write(0, 8, '发货地址', style_heading)
    sheet.write(0, 9, '收货单位', style_heading)
    sheet.write(0, 10, '油品', style_heading)
    sheet.write(0, 11, '车次', style_heading)
    sheet.write(0, 12, '车舱编号', style_heading)
    sheet.write(0, 13, '支付金额', style_heading)
    sheet.write(0, 14, '实发量', style_heading)
    sheet.write(0, 15, '审核状态', style_heading)
    sheet.write(0, 16, '审核人', style_heading)
    sheet.write(0, 17, '备注', style_heading)

    # 写入数据
    data_row = 1
    count = 1
    for i in information_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i.inside_number)
        sheet.write(data_row, 2, i.outside_number)
        sheet.write(data_row, 3, i.customer.name)
        # 转化时间格式
        sheet.write(data_row, 4, i.deliver_time, datastyle)
        sheet.write(data_row, 5, i.car.name)
        sheet.write(data_row, 6, i.car.driver.username)
        sheet.write(data_row, 7, i.car.supercargo.username)
        sheet.write(data_row, 8, i.oilwarehouse.name)
        sheet.write(data_row, 9, i.petrolstation.name)
        sheet.write(data_row, 10, i.oil.name)
        sheet.write(data_row, 11, i.get_drive_number_display())
        sheet.write(data_row, 12, i.get_cabin_display())
        sheet.write(data_row, 13, i.price)
        sheet.write(data_row, 14, i.paid_in_number)
        sheet.write(data_row, 15, i.get_status_audit_display())
        sheet.write(data_row, 16, i.auditor)
        sheet.write(data_row, 17, i.remark)
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出运费结算
def export_settlement(request):
    # 获取搜索字段
    field = request.GET.get("field")
    # 获取搜索条件
    q = request.GET.get("q")
    # 获取全部工资信息
    staticinformation_list = models.StaticInformation.objects.all().order_by("-deliver_time", "car_name",
                                                                             "drive_number", "cabin")
    # 如果q有值
    if q:
        # 如果获取的是配送时间
        if field == "deliver_time":
            # 如果是单个时间
            if q.find(":") == -1:
                staticinformation_list = models.StaticInformation.objects.filter(deliver_time=q).order_by(
                    "-deliver_time",
                    "car_name",
                    "drive_number",
                    "cabin")
            # 如果是时间段
            else:
                start_time_str, end_time_str = q.split(":")
                start_time_str = start_time_str.strip()
                end_time_str = end_time_str.strip()
                staticinformation_list = models.StaticInformation.objects.filter(
                    deliver_time__range=(start_time_str, end_time_str)).order_by(
                    "-deliver_time",
                    "car_name",
                    "drive_number",
                    "cabin")

        # 如果获取的是车号
        elif field == "car_name":
            staticinformation_list = models.StaticInformation.objects.filter(car_name=q).order_by("-deliver_time",
                                                                                                  "car_name",
                                                                                                  "drive_number",
                                                                                                  "cabin")
        # 如果获取的是外部单号
        elif field == "outside_number":
            staticinformation_list = models.StaticInformation.objects.filter(outside_number=q).order_by("-deliver_time",
                                                                                                        "car_name",
                                                                                                        "drive_number",
                                                                                                        "cabin")
        # 如果获取的是内部单号
        elif field == "inside_number":
            staticinformation_list = models.StaticInformation.objects.filter(inside_number=q).order_by("-deliver_time",
                                                                                                       "car_name",
                                                                                                       "drive_number",
                                                                                                       "cabin")
        # 如果获取的是驾驶员
        elif field == "driver_name":
            staticinformation_list = models.StaticInformation.objects.filter(driver=q).order_by("-deliver_time",
                                                                                                "car_name",
                                                                                                "drive_number", "cabin")
        # 如果获取的是押运员
        elif field == "supercargo_name":
            staticinformation_list = models.StaticInformation.objects.filter(supercargo=q).order_by("-deliver_time",
                                                                                                    "car_name",
                                                                                                    "drive_number",
                                                                                                    "cabin")
        # 如果获取的是发货单位
        elif field == "customer_name":
            staticinformation_list = models.StaticInformation.objects.filter(customer_name=q).order_by("-deliver_time",
                                                                                                       "car_name",
                                                                                                       "drive_number",
                                                                                                       "cabin")
    else:
        # 如果没有获取到q,则导出全部数据
        staticinformation_list = models.StaticInformation.objects.all().order_by("-deliver_time", "car_name",
                                                                                 "drive_number", "cabin")

    # 日期格式
    datastyle = xlwt.XFStyle()
    datastyle.num_format_str = 'yyyy-mm-dd'
    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    sheet.col(5).width = 256 * 15
    sheet.col(6).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '内部编号', style_heading)
    sheet.write(0, 2, '外部编号', style_heading)
    sheet.write(0, 3, '发货油库', style_heading)
    sheet.write(0, 4, '配送时间', style_heading)
    sheet.write(0, 5, '车号', style_heading)
    sheet.write(0, 6, '驾驶员', style_heading)
    sheet.write(0, 7, '押运员', style_heading)
    sheet.write(0, 8, '发货油库', style_heading)
    sheet.write(0, 9, '收货单位', style_heading)
    sheet.write(0, 10, '油品', style_heading)
    # sheet.write(0, 11, '车次', style_heading)
    # sheet.write(0, 12, '车舱编号', style_heading)
    # sheet.write(0, 13, '支付金额', style_heading)
    sheet.write(0, 11, '实发量', style_heading)
    sheet.write(0, 12, '运距', style_heading)
    # sheet.write(0, 16, '短程标准', style_heading)
    sheet.write(0, 13, '短程单价', style_heading)
    sheet.write(0, 14, '长程单价', style_heading)
    sheet.write(0, 15, '短程运费', style_heading)
    sheet.write(0, 16, '长程运费', style_heading)
    sheet.write(0, 17, '运费合计', style_heading)
    sheet.write(0, 18, '备注', style_heading)

    # 写入数据
    data_row = 1
    count = 1
    for i in staticinformation_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i.inside_number)
        sheet.write(data_row, 2, i.outside_number)
        sheet.write(data_row, 3, i.customer_name)
        # 转化时间格式
        sheet.write(data_row, 4, i.deliver_time, datastyle)
        sheet.write(data_row, 5, i.car_name)
        sheet.write(data_row, 6, i.driver)
        sheet.write(data_row, 7, i.supercargo)
        sheet.write(data_row, 8, i.oilwarehouse)
        sheet.write(data_row, 9, i.petrolstation)
        sheet.write(data_row, 10, i.oil)
        # sheet.write(data_row, 11, i.drive_number)
        # sheet.write(data_row, 12, i.cabin)
        # sheet.write(data_row, 13, i.price)
        sheet.write(data_row, 11, i.paid_in_number)
        # 客户里程
        sheet.write(data_row, 12, i.customer_mileage)
        # sheet.write(data_row, 16, i.shortmileage_standard)
        sheet.write(data_row, 13, i.shortmileage_price)
        sheet.write(data_row, 14, i.longmileage_price)
        sheet.write(data_row, 15, i.short_price)
        sheet.write(data_row, 16, i.long_price)
        sheet.write(data_row, 17, i.long_price + i.short_price)
        sheet.write(data_row, 18, i.remark)
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


##导出重复工资列表信息
def export_earning(request):
    # 获取搜索字段
    field = request.GET.get("field")
    # 获取搜索条件
    q = request.GET.get("q")
    # 执行原生的sql语句,获取全部的不去重数据
    staticinformation_list = models.StaticInformation.objects.raw(
        "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
    )
    # 如果有搜索内容
    if q:
        # 如果搜索条件是配送时间
        if field == "deliver_time":
            # 如果是单个时间
            if q.find(":") == -1:
                # 执行原生的sql语句,获取全部的不去重数据
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where deliver_time=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [q]
                )
            # 如果是时间段
            else:
                start_time_str, end_time_str = q.split(":")
                start_time_str = start_time_str.strip()
                end_time_str = end_time_str.strip()
                # 执行原生的sql语句,获取全部的不去重数据
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where deliver_time between %s and %s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [start_time_str, end_time_str]
                )

        # 如果搜索条件是车号
        elif field == "car_name":
            # 执行原生的sql语句,获取全部的不去重数据
            staticinformation_list = models.StaticInformation.objects.raw(
                "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where car_name=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                [q]
            )
        # 如果搜索条件是驾驶员
        elif field == "driver":
            # 执行原生的sql语句,获取全部的不去重数据
            staticinformation_list = models.StaticInformation.objects.raw(
                "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where driver=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                [q]
            )
        # 如果搜索条件是车号
        elif field == "supercargo":
            # 执行原生的sql语句,获取全部的不去重数据
            staticinformation_list = models.StaticInformation.objects.raw(
                "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where supercargo=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                [q]
            )
    else:
        # 执行原生的sql语句,获取全部的不去重数据
        staticinformation_list = models.StaticInformation.objects.raw(
            "select salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(salary_staticinformation.mileage separator '/') as mileage, group_concat(salary_staticinformation.customer_name separator '/') as customer_name,group_concat(salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
        )

    # 日期格式
    datastyle = xlwt.XFStyle()
    datastyle.num_format_str = 'yyyy-mm-dd'
    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                    font:
                        name Arial,
                        colour_index white,
                        bold on,
                        height 0xA0;
                    align:
                        wrap off,
                        vert center,
                        horiz center;
                    pattern:
                        pattern solid,
                        fore-colour 0x19;
                    borders:
                        left THIN,
                        right THIN,
                        top THIN,
                        bottom THIN;
                    """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    sheet.col(5).width = 256 * 15
    sheet.col(6).width = 256 * 15
    sheet.col(7).width = 256 * 15
    sheet.col(8).width = 256 * 15
    sheet.col(9).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '驾驶员', style_heading)
    sheet.write(0, 2, '押运员', style_heading)
    sheet.write(0, 3, '车号', style_heading)
    sheet.write(0, 4, '配送时间', style_heading)
    sheet.write(0, 5, '车次', style_heading)
    sheet.write(0, 6, '发货单位', style_heading)
    sheet.write(0, 7, '运距', style_heading)
    sheet.write(0, 8, '发货地址', style_heading)
    sheet.write(0, 9, '收货单位', style_heading)

    # 写入数据
    data_row = 1
    count = 1
    for i in staticinformation_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i.driver)
        sheet.write(data_row, 2, i.supercargo)
        sheet.write(data_row, 3, i.car_name)
        # 转化时间格式
        sheet.write(data_row, 4, i.deliver_time, datastyle)
        sheet.write(data_row, 5, i.drive_number)
        sheet.write(data_row, 6, i.customer_name)
        sheet.write(data_row, 7, i.mileage)
        sheet.write(data_row, 8, i.oilwarehouse)
        sheet.write(data_row, 9, i.petrolstation)
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出去重后的工资信息表
def export_earning_distinct(request):
    # 获取搜索字段
    field = request.GET.get("field")
    # 获取搜索条件
    q = request.GET.get("q")
    # 执行原生的sql语句
    staticinformation_list = models.StaticInformation.objects.raw(
        "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number,salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
    )

    # 如果有搜索内容
    if q:
        # 如果搜索条件是配送时间
        if field == "deliver_time":
            # 如果是单个时间
            if q.find(":") == -1:
                # 执行原生的sql语句
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where deliver_time=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [q]
                )
            else:
                start_time_str, end_time_str = q.split(":")
                start_time_str = start_time_str.strip()
                end_time_str = end_time_str.strip()
                # 执行原生的sql语句
                staticinformation_list = models.StaticInformation.objects.raw(
                    "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where deliver_time between %s and %s group by driver,deliver_time,drive_number order by deliver_time desc",
                    [start_time_str, end_time_str]
                )


        # 如果搜索条件是车号
        elif field == "car_name":
            # 执行原生的sql语句
            staticinformation_list = models.StaticInformation.objects.raw(
                "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where car_name=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                [q]
            )
        # 如果搜索条件是驾驶员
        elif field == "driver":
            # 执行原生的sql语句
            staticinformation_list = models.StaticInformation.objects.raw(
                "select salary_staticinformation.car_type as car_type, salary_staticinformation.earning as earning, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where driver=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                [q]
            )
        # 如果搜索条件是押运员
        elif field == "supercargo":
            # 执行原生的sql语句
            staticinformation_list = models.StaticInformation.objects.raw(
                "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation where supercargo=%s group by driver,deliver_time,drive_number order by deliver_time desc",
                [q]
            )
    # 遍历sql语句
    for distinct_information in staticinformation_list:
        # 分隔去重后的加油站
        distinct_petrolstation_list = distinct_information.petrolstation.split("/")
        # 分隔去重后的油库
        distinct_oilwarehouse_list = distinct_information.oilwarehouse.split("/")
        # 分隔去重后的里程(求出最大的里程数)
        mileage_list = distinct_information.mileage.split("/")
        mileage_list = [int(x) for x in mileage_list]
        distinct_information.max_mileage = max(mileage_list)

        # 计算分割后的加油站个数
        petrolstation_count = len(distinct_petrolstation_list) - 1
        # 计算分割后的加油站个数
        oilwarehouse_count = len(distinct_oilwarehouse_list) - 1
        # 计算分割后的加油站油库/个数
        distinct_information.oilwarehouse_petrolstation_count = petrolstation_count + oilwarehouse_count
        #######(工资等于去重后的加油站个数-1)*12
        distinct_information.earning += (petrolstation_count + oilwarehouse_count) * 12
        # 获取一车的油罐数
        oiltank_number_list = distinct_information.oiltank_number.split("/")
        # print("oiltank_number_list", oiltank_number_list)
        for oiltank_number in oiltank_number_list:
            distinct_information.earning += int(oiltank_number) * 2
        #########################按车型的工资
        # 如果车型是20吨的车
        if distinct_information.car_type == "20吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 将列表中的字符串都转化成int类型,便于作比较
            mileage_list = [int(x) for x in mileage_list]
            # 如果一车中最大的里程小于36公里,就是53
            if max(mileage_list) < 36:
                distinct_information.earning += 50
            # 否则里程*0.6+29
            else:
                distinct_information.earning += Decimal(29 + max(mileage_list) * 0.6).quantize(
                    Decimal('0.00'))
        # 如果车型是30吨的车
        elif distinct_information.car_type == "30吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 将列表中的字符串都转化成int类型,便于作比较
            mileage_list = [int(x) for x in mileage_list]
            # 如果一车中最大的里程小于36公里,就是60
            if max(mileage_list) < 36:
                distinct_information.earning += 60
            # 否则里程*0.9+39
            else:
                distinct_information.earning += Decimal(39 + max(mileage_list) * 0.9).quantize(
                    Decimal('0.00'))
        # 如果车型是 33吨的车
        elif distinct_information.car_type == "33吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 将列表中的字符串都转化成int类型,便于作比较
            mileage_list = [int(x) for x in mileage_list]
            # 如果一车中最大的里程小于36公里,就是63
            if max(mileage_list) < 36:
                distinct_information.earning += 63
            # 否则里程*0.95+42
            else:
                distinct_information.earning += Decimal(42 + max(mileage_list) * 0.95).quantize(
                    Decimal('0.00'))

        # 获取所有12元加油站对象######################12元加油站
        petrolstation12_list = models.Petrolstation12.objects.all()
        # 获取所有12元加油站的名称集合
        petrolstation12_name_list = []
        for petrolstation12 in petrolstation12_list:
            petrolstation12_name_list.append(petrolstation12.name)
        # print(petrolstation12_name_list)
        # 获取所有30元加油站对象######################30元加油站
        petrolstation30_list = models.Petrolstation30.objects.all()
        # 获取所有30元加油站的名称集合
        petrolstation30_name_list = []
        for petrolstation30 in petrolstation30_list:
            petrolstation30_name_list.append(petrolstation30.name)

        # 获取当前的去重加油站
        petrolstation_list = distinct_information.petrolstation.split("/")
        # 求两个列表的交集
        list3 = list(set(petrolstation12_name_list).intersection(set(petrolstation_list)))
        list4 = list(set(petrolstation30_name_list).intersection(set(petrolstation_list)))
        # 如果有交集：
        # 如果即在12元又有30元，就只加30
        if list4 and list3:
            distinct_information.earning += 30
        # 如果只有12元，就只加12元
        elif list3:
            distinct_information.earning += 12
        # 如果只有30元，就只加30元
        elif list4:
            distinct_information.earning += 30
        ###########加油站1为: 大唐/仙鹤/吕港   加油站2为:  城北/南苑/粮运/北新/东郊/
        ##############如果加油站1 和加油站站2中都有一个,工资就加30
        list5 = ["大唐", "鹤洋", "吕港"]
        list6 = ["城北", "南苑", "粮运", "北新", "东郊"]
        new_list5 = list(set(list5).intersection(set(petrolstation_list)))
        new_list6 = list(set(list6).intersection(set(petrolstation_list)))
        if new_list5 and new_list6:
            distinct_information.earning += 30

    # 日期格式
    datastyle = xlwt.XFStyle()
    datastyle.num_format_str = 'yyyy-mm-dd'
    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                        font:
                            name Arial,
                            colour_index white,
                            bold on,
                            height 0xA0;
                        align:
                            wrap off,
                            vert center,
                            horiz center;
                        pattern:
                            pattern solid,
                            fore-colour 0x19;
                        borders:
                            left THIN,
                            right THIN,
                            top THIN,
                            bottom THIN;
                        """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    sheet.col(5).width = 256 * 15
    sheet.col(6).width = 256 * 15
    sheet.col(7).width = 256 * 15
    sheet.col(8).width = 256 * 15
    sheet.col(9).width = 256 * 15
    sheet.col(10).width = 256 * 15
    sheet.col(11).width = 256 * 15
    sheet.col(12).width = 256 * 15
    sheet.col(13).width = 256 * 15
    sheet.col(14).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '车号', style_heading)
    sheet.write(0, 2, '车次', style_heading)
    sheet.write(0, 3, '配送时间', style_heading)
    sheet.write(0, 4, '发货单位', style_heading)
    sheet.write(0, 5, '发货地址', style_heading)
    sheet.write(0, 6, '收货单位', style_heading)
    sheet.write(0, 7, '运距', style_heading)
    sheet.write(0, 8, '运距(最大值)', style_heading)
    sheet.write(0, 9, '油库加油站/个数(去重)', style_heading)
    sheet.write(0, 10, '油罐数', style_heading)
    sheet.write(0, 11, '驾驶员', style_heading)
    sheet.write(0, 12, '驾驶员工资', style_heading)
    sheet.write(0, 13, '押运员', style_heading)
    sheet.write(0, 14, '押运员工资', style_heading)
    # 写入数据
    data_row = 1
    count = 1
    for i in staticinformation_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i.car_name)
        sheet.write(data_row, 2, i.drive_number)
        # 转化时间格式
        sheet.write(data_row, 3, i.deliver_time, datastyle)
        sheet.write(data_row, 4, i.customer_name)
        sheet.write(data_row, 5, i.oilwarehouse)
        sheet.write(data_row, 6, i.petrolstation)
        sheet.write(data_row, 7, i.mileage)
        sheet.write(data_row, 8, i.max_mileage)
        sheet.write(data_row, 9, i.oilwarehouse_petrolstation_count)
        sheet.write(data_row, 10, i.oiltank_number)
        sheet.write(data_row, 11, i.driver)
        sheet.write(data_row, 12, i.earning)
        sheet.write(data_row, 13, i.supercargo)
        sheet.write(data_row, 14, round((i.earning) * Decimal(0.55), 2))
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


# 驾驶员每月工资函数的CBV
@method_decorator(login_required, name='get')
class DriverMonthSalaryView(View):
    def get(self, request):
        # 获取搜索条件
        field = request.GET.get("field")
        # 获取搜索内容
        q = request.GET.get("q")
        # 执行原生的sql语句,获取到分组工资后的数据列表
        staticinformation_list = models.StaticInformation.objects.raw(
            "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
        )
        # 遍历sql语句
        for distinct_information in staticinformation_list:
            # 分隔去重后的加油站
            distinct_petrolstation_list = distinct_information.petrolstation.split("/")
            # 分隔去重后的油库
            distinct_oilwarehouse_list = distinct_information.oilwarehouse.split("/")
            # 计算分割后的加油站个数
            petrolstation_count = len(distinct_petrolstation_list) - 1
            # 计算分割后的加油站个数
            oilwarehouse_count = len(distinct_oilwarehouse_list) - 1
            # 计算分割后的加油站油库/个数
            distinct_information.oilwarehouse_petrolstation_count = petrolstation_count + oilwarehouse_count
            #######(工资等于去重后的加油站个数-1)*12
            distinct_information.earning += (petrolstation_count + oilwarehouse_count) * 12
            # 获取一车的油罐数
            oiltank_number_list = distinct_information.oiltank_number.split("/")
            # print("oiltank_number_list", oiltank_number_list)
            for oiltank_number in oiltank_number_list:
                distinct_information.earning += int(oiltank_number) * 2
            #########################按车型的工资
            # 如果车型是20吨的车
            if distinct_information.car_type == "20吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 如果一车中最大的里程小于36公里,就是53
                if int(max(mileage_list)) < 36:
                    distinct_information.earning += 50
                # 否则里程*0.6+29
                else:
                    distinct_information.earning += Decimal(29 + int(max(mileage_list)) * 0.6).quantize(
                        Decimal('0.00'))
            # 如果车型是30吨的车
            elif distinct_information.car_type == "30吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 如果一车中最大的里程小于36公里,就是60
                if int(max(mileage_list)) < 36:
                    distinct_information.earning += 60
                # 否则里程*0.9+39
                else:
                    distinct_information.earning += Decimal(39 + int(max(mileage_list)) * 0.9).quantize(
                        Decimal('0.00'))
            # 如果车型是 33吨的车
            elif distinct_information.car_type == "33吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 如果一车中最大的里程小于36公里,就是63
                if int(max(mileage_list)) < 36:
                    distinct_information.earning += 63
                # 否则里程*0.95+42
                else:
                    distinct_information.earning += Decimal(42 + int(max(mileage_list)) * 0.95).quantize(
                        Decimal('0.00'))

            # 获取所有12元加油站对象######################12元加油站
            petrolstation12_list = models.Petrolstation12.objects.all()
            # 获取所有12元加油站的名称集合
            petrolstation12_name_list = []
            for petrolstation12 in petrolstation12_list:
                petrolstation12_name_list.append(petrolstation12.name)
            # print(petrolstation12_name_list)
            # 获取所有30元加油站对象######################30元加油站
            petrolstation30_list = models.Petrolstation30.objects.all()
            # 获取所有30元加油站的名称集合
            petrolstation30_name_list = []
            for petrolstation30 in petrolstation30_list:
                petrolstation30_name_list.append(petrolstation30.name)

            # 获取当前的去重加油站
            petrolstation_list = distinct_information.petrolstation.split("/")
            # 求两个列表的交集
            list3 = list(set(petrolstation12_name_list).intersection(set(petrolstation_list)))
            list4 = list(set(petrolstation30_name_list).intersection(set(petrolstation_list)))
            # 如果有交集：
            # 如果即在12元又有30元，就只加30
            if list4 and list3:
                distinct_information.earning += 30
            # 如果只有12元，就只加12元
            elif list3:
                distinct_information.earning += 12
            # 如果只有30元，就只加30元
            elif list4:
                distinct_information.earning += 30

            ###########加油站1为: 大唐/仙鹤/吕港   加油站2为:  城北/南苑/粮运/北新/东郊/
            ##############如果加油站1 和加油站站2中都有一个,工资就加30
            list5 = ["大唐", "鹤洋", "吕港"]
            list6 = ["城北", "南苑", "粮运", "北新", "东郊"]
            new_list5 = list(set(list5).intersection(set(petrolstation_list)))
            new_list6 = list(set(list6).intersection(set(petrolstation_list)))
            if new_list5 and new_list6:
                distinct_information.earning += 30

        for staticinformation in staticinformation_list:
            # 获取每月工资的对象(必须按照车号,车次,驾驶员,配送时间过滤)
            monthsalary_list = models.MonthSalary.objects.filter(car_name=staticinformation.car_name,
                                                                 drive_number=staticinformation.drive_number,
                                                                 driver_name=staticinformation.driver,
                                                                 deliver_time=staticinformation.deliver_time,
                                                                 )

            # 如果没有查询到每月的工资对象就新建
            if not monthsalary_list:
                models.MonthSalary.objects.create(car_name=staticinformation.car_name,
                                                  drive_number=staticinformation.drive_number,
                                                  driver_name=staticinformation.driver,
                                                  deliver_time=staticinformation.deliver_time,
                                                  supercargo_name=staticinformation.supercargo,
                                                  driver_salary=staticinformation.earning,
                                                  supercargo_salary=round(float(staticinformation.earning) * 0.55,
                                                                          2)
                                                  )
            else:
                # 存在就更新
                monthsalary_list.update(
                    driver_salary=staticinformation.earning,
                    supercargo_salary=round(float(staticinformation.earning) * 0.55,
                                            2)
                )

        # 查询出每个驾驶员每月的工资总和
        driver_monthsalary_list = models.MonthSalary.objects.values("driver_name", "deliver_time__month",
                                                                    "deliver_time__year",
                                                                    "deliver_time__year").annotate(
            monthsalary_sum=Sum("driver_salary")).values("driver_name", "monthsalary_sum", "deliver_time__month",
                                                         "deliver_time__year").order_by("deliver_time__month",
                                                                                        "deliver_time__year")
        try:
            # 如果有搜索内容:
            if q:
                # 如果搜索的字段是驾驶员
                if field == 'driver_name':
                    driver_monthsalary_list = driver_monthsalary_list.filter(driver_name=q)
                # 如果搜索的字段是年份
                elif field == 'deliver_year':
                    driver_monthsalary_list = driver_monthsalary_list.filter(deliver_time__year=q)
                # 如果搜索的字段是月份
                elif field == 'deliver_month':
                    driver_monthsalary_list = driver_monthsalary_list.filter(deliver_time__month=q)
        except Exception as e:
            return HttpResponse("选择字段错误,请重新选择!")

        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, len(driver_monthsalary_list), request)
        # 生成每一页的初始页和结束页
        driver_monthsalary_list = driver_monthsalary_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()

        q = request.GET.get("q")
        field = request.GET.get("field")
        return render(request, "month_salary/driver_month_salary.html",
                      {"page_num": page_num, "driver_monthsalary_list": driver_monthsalary_list,
                       "pagination": pagination,
                       "information_notes": information_notes, "q": q, "field": field})


# 押运员每月工资函数的CBV
@method_decorator(login_required, name='get')
class SupercargoMonthSalaryView(View):
    def get(self, request):
        # 获取搜索条件
        field = request.GET.get("field")
        # 获取搜索内容
        q = request.GET.get("q")
        # 执行原生的sql语句
        staticinformation_list = models.StaticInformation.objects.raw(
            "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
        )
        # 遍历sql语句
        for distinct_information in staticinformation_list:
            # 分隔去重后的加油站
            distinct_petrolstation_list = distinct_information.petrolstation.split("/")
            # 分隔去重后的油库
            distinct_oilwarehouse_list = distinct_information.oilwarehouse.split("/")

            # 计算分割后的加油站个数
            petrolstation_count = len(distinct_petrolstation_list) - 1
            # 计算分割后的加油站个数
            oilwarehouse_count = len(distinct_oilwarehouse_list) - 1
            # 计算分割后的加油站油库/个数
            distinct_information.oilwarehouse_petrolstation_count = petrolstation_count + oilwarehouse_count
            #######(工资等于去重后的加油站个数-1)*12
            distinct_information.earning += (petrolstation_count + oilwarehouse_count) * 12
            # 获取一车的油罐数
            oiltank_number_list = distinct_information.oiltank_number.split("/")
            # print("oiltank_number_list", oiltank_number_list)
            for oiltank_number in oiltank_number_list:
                distinct_information.earning += int(oiltank_number) * 2
            #########################按车型的工资
            # 如果车型是20吨的车
            if distinct_information.car_type == "20吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 如果一车中最大的里程小于36公里,就是50
                if int(max(mileage_list)) < 36:
                    distinct_information.earning += 50
                # 否则里程*0.6+29
                else:
                    distinct_information.earning += Decimal(29 + int(max(mileage_list)) * 0.6).quantize(
                        Decimal('0.00'))
            # 如果车型是30吨的车
            elif distinct_information.car_type == "30吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 如果一车中最大的里程小于36公里,就是60
                if int(max(mileage_list)) < 36:
                    distinct_information.earning += 60
                # 否则里程*0.9+39
                else:
                    distinct_information.earning += Decimal(39 + int(max(mileage_list)) * 0.9).quantize(
                        Decimal('0.00'))
            # 如果车型是 33吨的车
            elif distinct_information.car_type == "33吨的车":
                # 获取里程列表
                mileage_list = distinct_information.mileage.split("/")
                # 如果一车中最大的里程小于36公里,就是63
                if int(max(mileage_list)) < 36:
                    distinct_information.earning += 63
                # 否则里程*0.95+42
                else:
                    distinct_information.earning += Decimal(42 + int(max(mileage_list)) * 0.95).quantize(
                        Decimal('0.00'))

            # 获取所有12元加油站对象######################12元加油站
            petrolstation12_list = models.Petrolstation12.objects.all()
            # 获取所有12元加油站的名称集合
            petrolstation12_name_list = []
            for petrolstation12 in petrolstation12_list:
                petrolstation12_name_list.append(petrolstation12.name)
            # print(petrolstation12_name_list)
            # 获取所有30元加油站对象######################30元加油站
            petrolstation30_list = models.Petrolstation30.objects.all()
            # 获取所有30元加油站的名称集合
            petrolstation30_name_list = []
            for petrolstation30 in petrolstation30_list:
                petrolstation30_name_list.append(petrolstation30.name)

            # 获取当前的去重加油站
            petrolstation_list = distinct_information.petrolstation.split("/")
            # 求两个列表的交集
            list3 = list(set(petrolstation12_name_list).intersection(set(petrolstation_list)))
            list4 = list(set(petrolstation30_name_list).intersection(set(petrolstation_list)))
            # 如果有交集：
            # 如果即在12元又有30元，就只加30
            if list4 and list3:
                distinct_information.earning += 30
            # 如果只有12元，就只加12元
            elif list3:
                distinct_information.earning += 12
            # 如果只有30元，就只加30元
            elif list4:
                distinct_information.earning += 30
            ###########加油站1为: 大唐/仙鹤/吕港   加油站2为:  城北/南苑/粮运/北新/东郊/
            ##############如果加油站1 和加油站站2中都有一个,工资就加30
            list5 = ["大唐", "鹤洋", "吕港"]
            list6 = ["城北", "南苑", "粮运", "北新", "东郊"]
            new_list5 = list(set(list5).intersection(set(petrolstation_list)))
            new_list6 = list(set(list6).intersection(set(petrolstation_list)))
            if new_list5 and new_list6:
                distinct_information.earning += 30
        for staticinformation in staticinformation_list:
            monthsalary_list = models.MonthSalary.objects.filter(car_name=staticinformation.car_name,
                                                                 drive_number=staticinformation.drive_number,
                                                                 driver_name=staticinformation.driver,
                                                                 deliver_time=staticinformation.deliver_time
                                                                 )
            # 如果没有查询到每月的工资对象就新建
            if not monthsalary_list:
                models.MonthSalary.objects.create(car_name=staticinformation.car_name,
                                                  drive_number=staticinformation.drive_number,
                                                  driver_name=staticinformation.driver,
                                                  deliver_time=staticinformation.deliver_time,
                                                  supercargo_name=staticinformation.supercargo,
                                                  driver_salary=staticinformation.earning,
                                                  supercargo_salary=round(float(staticinformation.earning) * 0.55,
                                                                          2)
                                                  )
            else:
                # 有就更新(只能更新queryset列表,一个对象没有update方法)
                monthsalary_list.update(
                    driver_salary=staticinformation.earning,
                    supercargo_salary=round(float(staticinformation.earning) * 0.55,
                                            2)
                )

        # 查询出每个押运员每月的工资总和
        supercargo_monthsalary_list = models.MonthSalary.objects.values("supercargo_name", "deliver_time__month",
                                                                        "deliver_time__year").annotate(
            monthsalary_sum=Sum("supercargo_salary")).values("supercargo_name", "monthsalary_sum",
                                                             "deliver_time__month", "deliver_time__year").order_by(
            "deliver_time__month", "deliver_time__year")
        # 如果选择框选择错误
        try:
            # 如果有搜索内容:
            if q:

                # 如果搜索的字段是驾驶员
                if field == 'supercargo_name':
                    supercargo_monthsalary_list = supercargo_monthsalary_list.filter(supercargo_name=q)
                # 如果搜索的字段是年份
                elif field == 'deliver_year':
                    supercargo_monthsalary_list = supercargo_monthsalary_list.filter(deliver_time__year=q)
                # 如果搜索的字段是月份
                elif field == 'deliver_month':
                    supercargo_monthsalary_list = supercargo_monthsalary_list.filter(deliver_time__month=q)
        except Exception as e:
            return HttpResponse("选择字段错误,请重新选择!")

        # 获取当前页码
        current_page_num = request.GET.get("page", 1)
        # 生成page对象
        pagination = page.Pagination(current_page_num, len(supercargo_monthsalary_list), request)
        # 生成每一页的初始页和结束页
        supercargo_monthsalary_list = supercargo_monthsalary_list[pagination.start:pagination.end]

        # 获取当前页面的page
        page_num = request.GET.get("page", 1)
        # 未审批的个数
        information_notes = models.Information.objects.filter(status_audit=1).count()

        q = request.GET.get("q")
        field = request.GET.get("field")
        return render(request, "month_salary/supercargo_month_salary.html",
                      {"page_num": page_num, "supercargo_monthsalary_list": supercargo_monthsalary_list,
                       "pagination": pagination,
                       "information_notes": information_notes, "q": q, "field": field})


# 导出驾驶员每月工资表
def export_driver_month_salary(request):
    # 获取搜索条件
    field = request.GET.get("field")
    # 获取搜索内容
    q = request.GET.get("q")
    # 执行原生的sql语句,获取到分组工资后的数据列表
    staticinformation_list = models.StaticInformation.objects.raw(
        "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
    )
    # 遍历sql语句
    for distinct_information in staticinformation_list:
        # 分隔去重后的加油站
        distinct_petrolstation_list = distinct_information.petrolstation.split("/")
        # 分隔去重后的油库
        distinct_oilwarehouse_list = distinct_information.oilwarehouse.split("/")
        # 计算分割后的加油站个数
        petrolstation_count = len(distinct_petrolstation_list) - 1
        # 计算分割后的加油站个数
        oilwarehouse_count = len(distinct_oilwarehouse_list) - 1
        # 计算分割后的加油站油库/个数
        distinct_information.oilwarehouse_petrolstation_count = petrolstation_count + oilwarehouse_count
        #######(工资等于去重后的加油站个数-1)*12
        distinct_information.earning += (petrolstation_count + oilwarehouse_count) * 12
        # 获取一车的油罐数
        oiltank_number_list = distinct_information.oiltank_number.split("/")
        # print("oiltank_number_list", oiltank_number_list)
        for oiltank_number in oiltank_number_list:
            distinct_information.earning += int(oiltank_number) * 2
        #########################按车型的工资
        # 如果车型是20吨的车
        if distinct_information.car_type == "20吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 如果一车中最大的里程小于36公里,就是53
            if int(max(mileage_list)) < 36:
                distinct_information.earning += 50
            # 否则里程*0.6+29
            else:
                distinct_information.earning += Decimal(29 + int(max(mileage_list)) * 0.6).quantize(
                    Decimal('0.00'))
        # 如果车型是30吨的车
        elif distinct_information.car_type == "30吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 如果一车中最大的里程小于36公里,就是60
            if int(max(mileage_list)) < 36:
                distinct_information.earning += 60
            # 否则里程*0.9+39
            else:
                distinct_information.earning += Decimal(39 + int(max(mileage_list)) * 0.9).quantize(
                    Decimal('0.00'))
        # 如果车型是 33吨的车
        elif distinct_information.car_type == "33吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 如果一车中最大的里程小于36公里,就是63
            if int(max(mileage_list)) < 36:
                distinct_information.earning += 63
            # 否则里程*0.95+42
            else:
                distinct_information.earning += Decimal(42 + int(max(mileage_list)) * 0.95).quantize(
                    Decimal('0.00'))

        # 获取所有12元加油站对象######################12元加油站
        petrolstation12_list = models.Petrolstation12.objects.all()
        # 获取所有12元加油站的名称集合
        petrolstation12_name_list = []
        for petrolstation12 in petrolstation12_list:
            petrolstation12_name_list.append(petrolstation12.name)
        # print(petrolstation12_name_list)
        # 获取所有30元加油站对象######################30元加油站
        petrolstation30_list = models.Petrolstation30.objects.all()
        # 获取所有30元加油站的名称集合
        petrolstation30_name_list = []
        for petrolstation30 in petrolstation30_list:
            petrolstation30_name_list.append(petrolstation30.name)

        # 获取当前的去重加油站
        petrolstation_list = distinct_information.petrolstation.split("/")
        # 求两个列表的交集
        list3 = list(set(petrolstation12_name_list).intersection(set(petrolstation_list)))
        list4 = list(set(petrolstation30_name_list).intersection(set(petrolstation_list)))
        # 如果有交集：
        # 如果即在12元又有30元，就只加30
        if list4 and list3:
            distinct_information.earning += 30
        # 如果只有12元，就只加12元
        elif list3:
            distinct_information.earning += 12
        # 如果只有30元，就只加30元
        elif list4:
            distinct_information.earning += 30
    for staticinformation in staticinformation_list:
        # 获取每月工资的对象(必须按照车号,车次,驾驶员,配送时间过滤)
        monthsalary_list = models.MonthSalary.objects.filter(car_name=staticinformation.car_name,
                                                             drive_number=staticinformation.drive_number,
                                                             driver_name=staticinformation.driver,
                                                             deliver_time=staticinformation.deliver_time,
                                                             )
        # 如果没有查询到每月的工资对象就新建
        if not monthsalary_list:
            models.MonthSalary.objects.create(car_name=staticinformation.car_name,
                                              drive_number=staticinformation.drive_number,
                                              driver_name=staticinformation.driver,
                                              deliver_time=staticinformation.deliver_time,
                                              supercargo_name=staticinformation.supercargo,
                                              driver_salary=staticinformation.earning,
                                              supercargo_salary=round(float(staticinformation.earning) * 0.55,
                                                                      2)
                                              )
        else:
            # 存在就更新
            monthsalary_list.update(
                driver_salary=staticinformation.earning,
                supercargo_salary=round(float(staticinformation.earning) * 0.55,
                                        2)
            )

    # 查询出每个驾驶员每月的工资总和
    driver_monthsalary_list = models.MonthSalary.objects.values("driver_name", "deliver_time__month",
                                                                "deliver_time__year",
                                                                "deliver_time__year").annotate(
        monthsalary_sum=Sum("driver_salary")).values("driver_name", "monthsalary_sum", "deliver_time__month",
                                                     "deliver_time__year").order_by("deliver_time__month",
                                                                                    "deliver_time__year")
    try:
        # 如果有搜索内容:
        if q:
            # 如果搜索的字段是驾驶员
            if field == 'driver_name':
                driver_monthsalary_list = driver_monthsalary_list.filter(driver_name=q)
            # 如果搜索的字段是年份
            elif field == 'deliver_year':
                driver_monthsalary_list = driver_monthsalary_list.filter(deliver_time__year=q)
            # 如果搜索的字段是月份
            elif field == 'deliver_month':
                driver_monthsalary_list = driver_monthsalary_list.filter(deliver_time__month=q)
    except Exception as e:
        return HttpResponse("选择字段错误,请重新选择!")
    driver_monthsalary_list = list(driver_monthsalary_list)
    # print("driver_monthsalary_list", driver_monthsalary_list)

    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                        font:
                            name Arial,
                            colour_index white,
                            bold on,
                            height 0xA0;
                        align:
                            wrap off,
                            vert center,
                            horiz center;
                        pattern:
                            pattern solid,
                            fore-colour 0x19;
                        borders:
                            left THIN,
                            right THIN,
                            top THIN,
                            bottom THIN;
                        """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '驾驶员', style_heading)
    sheet.write(0, 2, '配送年份', style_heading)
    sheet.write(0, 3, '配送月份', style_heading)
    sheet.write(0, 4, '工资汇总(每月)', style_heading)
    # 写入数据
    data_row = 1
    count = 1
    for i in driver_monthsalary_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i['driver_name'])
        sheet.write(data_row, 2, i['deliver_time__year'])
        # 转化时间格式
        sheet.write(data_row, 3, i['deliver_time__month'])
        sheet.write(data_row, 4, i['monthsalary_sum'])
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出押运员每月工资表
def export_supercargo_month_salary(request):
    # 获取搜索条件
    field = request.GET.get("field")
    # 获取搜索内容
    q = request.GET.get("q")
    # 执行原生的sql语句,获取到分组工资后的数据列表
    staticinformation_list = models.StaticInformation.objects.raw(
        "select salary_staticinformation.car_type as car_type, group_concat(salary_staticinformation.oiltank_number separator '/') as oiltank_number, salary_staticinformation.earning as earning, salary_staticinformation.id, salary_staticinformation.driver as driver, salary_staticinformation.supercargo as supercargo,salary_staticinformation.car_name as car_name,salary_staticinformation.deliver_time as deliver_time,salary_staticinformation.drive_number as drive_number, group_concat(distinct salary_staticinformation.customer_name separator '/') as customer_name, group_concat(distinct salary_staticinformation.mileage separator '/') as mileage, group_concat(distinct salary_staticinformation.oilwarehouse separator '/') as oilwarehouse, group_concat(distinct salary_staticinformation.petrolstation separator '/') as petrolstation from salary_staticinformation group by driver,deliver_time,drive_number order by deliver_time desc"
    )
    # 遍历sql语句
    for distinct_information in staticinformation_list:
        # 分隔去重后的加油站
        distinct_petrolstation_list = distinct_information.petrolstation.split("/")
        # 分隔去重后的油库
        distinct_oilwarehouse_list = distinct_information.oilwarehouse.split("/")
        # 计算分割后的加油站个数
        petrolstation_count = len(distinct_petrolstation_list) - 1
        # 计算分割后的加油站个数
        oilwarehouse_count = len(distinct_oilwarehouse_list) - 1
        # 计算分割后的加油站油库/个数
        distinct_information.oilwarehouse_petrolstation_count = petrolstation_count + oilwarehouse_count
        #######(工资等于去重后的加油站个数-1)*12
        distinct_information.earning += (petrolstation_count + oilwarehouse_count) * 12
        # 获取一车的油罐数
        oiltank_number_list = distinct_information.oiltank_number.split("/")
        # print("oiltank_number_list", oiltank_number_list)
        for oiltank_number in oiltank_number_list:
            distinct_information.earning += int(oiltank_number) * 2
        #########################按车型的工资
        # 如果车型是 20吨的车
        if distinct_information.car_type == "20吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 如果一车中最大的里程小于36公里,就是53
            if int(max(mileage_list)) < 36:
                distinct_information.earning += 50
            # 否则里程*0.6+29
            else:
                distinct_information.earning += Decimal(29 + int(max(mileage_list)) * 0.6).quantize(
                    Decimal('0.00'))
        # 如果车型是30吨的车
        elif distinct_information.car_type == "30吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 如果一车中最大的里程小于36公里,就是60
            if int(max(mileage_list)) < 36:
                distinct_information.earning += 60
            # 否则里程*0.9+39
            else:
                distinct_information.earning += Decimal(39 + int(max(mileage_list)) * 0.9).quantize(
                    Decimal('0.00'))
        # 如果车型是 33吨的车
        elif distinct_information.car_type == "33吨的车":
            # 获取里程列表
            mileage_list = distinct_information.mileage.split("/")
            # 如果一车中最大的里程小于36公里,就是63
            if int(max(mileage_list)) < 36:
                distinct_information.earning += 63
            # 否则里程*0.95+42
            else:
                distinct_information.earning += Decimal(42 + int(max(mileage_list)) * 0.95).quantize(
                    Decimal('0.00'))

        # 获取所有12元加油站对象######################12元加油站
        petrolstation12_list = models.Petrolstation12.objects.all()
        # 获取所有12元加油站的名称集合
        petrolstation12_name_list = []
        for petrolstation12 in petrolstation12_list:
            petrolstation12_name_list.append(petrolstation12.name)
        # print(petrolstation12_name_list)
        # 获取所有30元加油站对象######################30元加油站
        petrolstation30_list = models.Petrolstation30.objects.all()
        # 获取所有30元加油站的名称集合
        petrolstation30_name_list = []
        for petrolstation30 in petrolstation30_list:
            petrolstation30_name_list.append(petrolstation30.name)

        # 获取当前的去重加油站
        petrolstation_list = distinct_information.petrolstation.split("/")
        # 求两个列表的交集
        list3 = list(set(petrolstation12_name_list).intersection(set(petrolstation_list)))
        list4 = list(set(petrolstation30_name_list).intersection(set(petrolstation_list)))
        # 如果有交集：
        # 如果即在12元又有30元，就只加30
        if list4 and list3:
            distinct_information.earning += 30
        # 如果只有12元，就只加12元
        elif list3:
            distinct_information.earning += 12
        # 如果只有30元，就只加30元
        elif list4:
            distinct_information.earning += 30
    for staticinformation in staticinformation_list:
        # 获取每月工资的对象(必须按照车号,车次,驾驶员,配送时间过滤)
        monthsalary_list = models.MonthSalary.objects.filter(car_name=staticinformation.car_name,
                                                             drive_number=staticinformation.drive_number,
                                                             driver_name=staticinformation.driver,
                                                             deliver_time=staticinformation.deliver_time,
                                                             )
        # 如果没有查询到每月的工资对象就新建
        if not monthsalary_list:
            models.MonthSalary.objects.create(car_name=staticinformation.car_name,
                                              drive_number=staticinformation.drive_number,
                                              driver_name=staticinformation.driver,
                                              deliver_time=staticinformation.deliver_time,
                                              supercargo_name=staticinformation.supercargo,
                                              driver_salary=staticinformation.earning,
                                              supercargo_salary=round(float(staticinformation.earning) * 0.55,
                                                                      2)
                                              )
        else:
            # 存在就更新
            monthsalary_list.update(
                driver_salary=staticinformation.earning,
                supercargo_salary=round(float(staticinformation.earning) * 0.55,
                                        2)
            )

    # 查询出每个押运员每月的工资总和
    supercargo_monthsalary_list = models.MonthSalary.objects.values("supercargo_name", "deliver_time__month",
                                                                    "deliver_time__year",
                                                                    "deliver_time__year").annotate(
        monthsalary_sum=Sum("supercargo_salary")).values("supercargo_name", "monthsalary_sum", "deliver_time__month",
                                                         "deliver_time__year").order_by("deliver_time__month",
                                                                                        "deliver_time__year")
    try:
        # 如果有搜索内容:
        if q:
            # 如果搜索的字段是押运员
            if field == 'supercargo_name':
                supercargo_monthsalary_list = supercargo_monthsalary_list.filter(supercargo_name=q)
            # 如果搜索的字段是年份
            elif field == 'deliver_year':
                supercargo_monthsalary_list = supercargo_monthsalary_list.filter(deliver_time__year=q)
            # 如果搜索的字段是月份
            elif field == 'deliver_month':
                supercargo_monthsalary_list = supercargo_monthsalary_list.filter(deliver_time__month=q)
    except Exception as e:
        return HttpResponse("选择字段错误,请重新选择!")
    supercargo_monthsalary_list = list(supercargo_monthsalary_list)
    # print("supercargo_monthsalary_list", supercargo_monthsalary_list)

    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                        font:
                            name Arial,
                            colour_index white,
                            bold on,
                            height 0xA0;
                        align:
                            wrap off,
                            vert center,
                            horiz center;
                        pattern:
                            pattern solid,
                            fore-colour 0x19;
                        borders:
                            left THIN,
                            right THIN,
                            top THIN,
                            bottom THIN;
                        """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '押运员', style_heading)
    sheet.write(0, 2, '配送年份', style_heading)
    sheet.write(0, 3, '配送月份', style_heading)
    sheet.write(0, 4, '工资汇总(每月)', style_heading)
    # 写入数据
    data_row = 1
    count = 1
    for i in supercargo_monthsalary_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i['supercargo_name'])
        sheet.write(data_row, 2, i['deliver_time__year'])
        # 转化时间格式
        sheet.write(data_row, 3, i['deliver_time__month'])
        sheet.write(data_row, 4, i['monthsalary_sum'])
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


# 驾驶员每月上班天数
def driver_month_work_days(request):
    # 按照驾驶员和配送时间进行分组
    staticInformation_list = models.StaticInformation.objects.values("driver", "deliver_time").annotate(
        c=Count(1)).values_list(
        "driver", "deliver_time__year", "deliver_time__month")
    # 将queryset转化成列表形式
    staticInformation_list = list(staticInformation_list)
    # print("staticInformation_list", staticInformation_list)
    ###############计算驾驶员每月的上班天数#################
    List = staticInformation_list
    a = {}
    for i in List:
        a[i] = List.count(i)
    # 获取搜索内容
    q = request.GET.get("q")
    # 获取搜索条件字段
    field = request.GET.get("field")
    # 异常处理
    try:
        # 如果有搜索内容
        if q:
            ##########如果搜索条件是押运员名字############
            if field == "driver_name":
                for key in list(a.keys()):
                    if key[0] != q:
                        del a[key]
            #########如果搜索条件是配送年份#############
            if field == "deliver_year":
                for key in list(a.keys()):
                    if key[1] != int(q):
                        del a[key]
            #########如果搜索条件是配送年份#############
            if field == "deliver_month":
                for key in list(a.keys()):
                    if key[2] != int(q):
                        del a[key]
    except Exception as e:
        return HttpResponse("选择操作有误")

    return render(request, "driver_month_work_days.html", {"a": a})


# 押运员每月上班天数函数
def supercargo_month_work_days(request):
    # 按照押运员和配送时间进行分组
    staticInformation_list = models.StaticInformation.objects.values("supercargo", "deliver_time").annotate(
        c=Count(1)).values_list(
        "supercargo", "deliver_time__year", "deliver_time__month")
    # 将queryset转化成列表形式
    staticInformation_list = list(staticInformation_list)
    # print("staticInformation_list", staticInformation_list)
    ###############计算押运员每月的上班天数#################
    List = staticInformation_list
    a = {}
    for i in List:
        a[i] = List.count(i)
    # 获取搜索内容
    q = request.GET.get("q")
    # 获取搜索条件字段
    field = request.GET.get("field")
    # 异常处理
    try:
        # 如果有搜索内容
        if q:
            ##########如果搜索条件是押运员名字############
            if field == "supercargo_name":
                for key in list(a.keys()):
                    if key[0] != q:
                        del a[key]
            #########如果搜索条件是配送年份#############
            if field == "deliver_year":
                for key in list(a.keys()):
                    if key[1] != int(q):
                        del a[key]
            #########如果搜索条件是配送年份#############
            if field == "deliver_month":
                for key in list(a.keys()):
                    if key[2] != int(q):
                        del a[key]
    except Exception as e:
        return HttpResponse("选择操作有误")

    return render(request, "supercargo_month_work_days.html", {"a": a, "q": q, "field": field})


# 导出押运员每月上班天数
def export_supercargo_month_work_days(request):
    # 按照押运员和配送时间进行分组
    staticInformation_list = models.StaticInformation.objects.values("supercargo", "deliver_time").annotate(
        c=Count(1)).values_list(
        "supercargo", "deliver_time__year", "deliver_time__month")
    # 将queryset转化成列表形式
    staticInformation_list = list(staticInformation_list)
    ###############计算押运员每月的上班天数#################
    List = staticInformation_list
    a = {}
    for i in List:
        a[i] = List.count(i)
    # 获取搜索内容
    q = request.GET.get("q")
    # 获取搜索条件字段
    field = request.GET.get("field")
    # 异常处理
    try:
        # 如果有搜索内容
        if q:
            ##########如果搜索条件是押运员名字############
            if field == "supercargo_name":
                for key in list(a.keys()):
                    if key[0] != q:
                        del a[key]
            #########如果搜索条件是配送年份#############
            if field == "deliver_year":
                for key in list(a.keys()):
                    if key[1] != int(q):
                        del a[key]
            #########如果搜索条件是配送年份#############
            if field == "deliver_month":
                for key in list(a.keys()):
                    if key[2] != int(q):
                        del a[key]
    except Exception as e:
        return HttpResponse("选择操作有误")

    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                        font:
                            name Arial,
                            colour_index white,
                            bold on,
                            height 0xA0;
                        align:
                            wrap off,
                            vert center,
                            horiz center;
                        pattern:
                            pattern solid,
                            fore-colour 0x19;
                        borders:
                            left THIN,
                            right THIN,
                            top THIN,
                            bottom THIN;
                        """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '押运员', style_heading)
    sheet.write(0, 2, '配送年份', style_heading)
    sheet.write(0, 3, '配送月份', style_heading)
    sheet.write(0, 4, '上班天数(每月)', style_heading)
    # 写入数据
    data_row = 1
    count = 1
    for k, v in a.items():
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, k[0])
        sheet.write(data_row, 2, k[1])
        # 转化时间格式
        sheet.write(data_row, 3, k[2])
        sheet.write(data_row, 4, v)
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出驾驶员每月上班天数
def export_driver_month_work_days(request):
    # 按照押运员和配送时间进行分组
    staticInformation_list = models.StaticInformation.objects.values("driver", "deliver_time").annotate(
        c=Count(1)).values_list(
        "driver", "deliver_time__year", "deliver_time__month")
    # 将queryset转化成列表形式
    staticInformation_list = list(staticInformation_list)
    ###############计算押运员每月的上班天数#################
    List = staticInformation_list
    a = {}
    for i in List:
        a[i] = List.count(i)
    # 获取搜索内容
    q = request.GET.get("q")
    # 获取搜索条件字段
    field = request.GET.get("field")
    # 异常处理
    try:
        # 如果有搜索内容
        if q:
            ##########如果搜索条件是押运员名字############
            if field == "driver_name":
                for key in list(a.keys()):
                    if key[0] != q:
                        del a[key]
            #########如果搜索条件是配送年份#############
            if field == "deliver_year":
                for key in list(a.keys()):
                    if key[1] != int(q):
                        del a[key]
            #########如果搜索条件是配送年份#############
            if field == "deliver_month":
                for key in list(a.keys()):
                    if key[2] != int(q):
                        del a[key]
    except Exception as e:
        return HttpResponse("选择操作有误")

    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                        font:
                            name Arial,
                            colour_index white,
                            bold on,
                            height 0xA0;
                        align:
                            wrap off,
                            vert center,
                            horiz center;
                        pattern:
                            pattern solid,
                            fore-colour 0x19;
                        borders:
                            left THIN,
                            right THIN,
                            top THIN,
                            bottom THIN;
                        """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '驾驶员', style_heading)
    sheet.write(0, 2, '配送年份', style_heading)
    sheet.write(0, 3, '配送月份', style_heading)
    sheet.write(0, 4, '上班天数(每月)', style_heading)
    # 写入数据
    data_row = 1
    count = 1
    for k, v in a.items():
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, k[0])
        sheet.write(data_row, 2, k[1])
        # 转化时间格式
        sheet.write(data_row, 3, k[2])
        sheet.write(data_row, 4, v)
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


# 导出全部加油站列表
def export_petrolstation(request):
    # 获取全部运费信息
    petrolstation_list = models.Petrolstation.objects.all()
    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    sheet.col(5).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '名称', style_heading)
    sheet.write(0, 2, '加油站编号', style_heading)
    sheet.write(0, 3, '客户', style_heading)
    sheet.write(0, 4, '备注', style_heading)

    # 写入数据
    data_row = 1
    count = 1
    for i in petrolstation_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i.name)
        sheet.write(data_row, 2, i.number)
        sheet.write(data_row, 3, i.customer.name)
        sheet.write(data_row, 4, i.remark)
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response

# 导出全部加油站油库里程列表
def export_petrolstation2oilwarehouse(request):
    # 获取全部运费信息
    petrolstation_list = models.Petrolstation2oilwarehouse.objects.all()
    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    sheet.col(5).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '员工里程', style_heading)
    sheet.write(0, 2, '客户里程', style_heading)
    sheet.write(0, 3, '油库', style_heading)
    sheet.write(0, 4, '加油站', style_heading)
    sheet.write(0, 5, '备注', style_heading)

    # 写入数据
    data_row = 1
    count = 1
    for i in petrolstation_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i.mileage)
        sheet.write(data_row, 2, i.customer_mileage)
        sheet.write(data_row, 3, i.oilwarehouse.name)
        sheet.write(data_row, 4, i.petrolstation.name)
        sheet.write(data_row, 5, i.remark)
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response

# 导出全部12元加油站列表
def export_petrolstation12(request):
    # 获取全部运费信息
    petrolstation_list = models.Petrolstation12.objects.all()
    # 设置HttpResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件类型
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet', cell_overwrite_ok=True)
    # 设置文件头的样式，这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
            font:
                name Arial,
                colour_index white,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid,
                fore-colour 0x19;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)
    # 设置列宽
    sheet.col(1).width = 256 * 15
    sheet.col(2).width = 256 * 15
    sheet.col(3).width = 256 * 15
    sheet.col(4).width = 256 * 15
    sheet.col(5).width = 256 * 15
    # 写入文件标题
    sheet.write(0, 0, '编号', style_heading)
    sheet.write(0, 1, '加油站名称', style_heading)
    sheet.write(0, 2, '备注', style_heading)

    # 写入数据
    data_row = 1
    count = 1
    for i in petrolstation_list:
        sheet.write(data_row, 0, count)
        sheet.write(data_row, 1, i.name)
        sheet.write(data_row, 2, i.remark)
        data_row = data_row + 1
        count += 1

    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response