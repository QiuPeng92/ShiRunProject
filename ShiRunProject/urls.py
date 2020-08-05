"""ShiRunProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
# 普通url使用path,含有正则re则使用re_path
from django.urls import path, re_path, include
# 导入salary应用下的views视图函数模块
from salary import views
# 导入media相关的工具包
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # 登录URL
    path('', views.index),
    #首页url
    re_path('^index/$', views.index),
    #每月运费url
    re_path('^freight/$', views.freight),
    # 登录URL
    re_path('^login/$', views.login, name="login"),
    # 注册URL
    re_path('^register/$', views.register, name="register"),
    # 注销URL
    re_path('^logout/$', views.logout, name="logout"),
    # media相关的url设置(static内部设置好了)
    re_path('media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),

    ################################用户URL##########################
    # 用户列表URl(CBV形式)
    re_path('^userinfo/list/$', views.UserinfoView.as_view(), name="userinfo_list"),
    # 添加用户URL(CBV形式)
    re_path('^userinfo/add/$', views.AddUserinfoView.as_view(), name="userinfo_add"),
    # 编辑客户URL(CBV形式)
    re_path('^userinfo/edit/(\d+)/$', views.EditUserinfoView.as_view(), name="userinfo_edit"),
    # 删除用户URL(CBV形式)
    re_path('^userinfo/delete/(?P<userinfo_delete_id>\d+)/$', views.userinfo_delete, name="userinfo_delete"),

    ################################客户URL##########################
    # 客户列表URL(FBV形式)
    # path('customer/list/', views.customer_list, name="customer_list"),
    # 客户列表URl(CBV形式)
    re_path('^customer/list/$', views.CustomerView.as_view(), name="customer_list"),
    # 添加客户URL(CBV形式)
    re_path('^customer/add/$', views.AddCustomerView.as_view(), name="customer_add"),
    # 编辑客户URL(CBV形式)
    re_path('^customer/edit/(\d+)/$', views.EditCustomerView.as_view(), name="customer_edit"),
    # 整合编辑删除URL
    # re_path('customer/edit/(\d+)', views.AddEdditCustomerView.as_view(), name="customer_edit"),
    # re_path('customer/add/', views.AddEdditCustomerView.as_view(), name="customer_add"),
    # 删除客户URL(CBV形式)
    re_path('^customer/delete/(?P<customer_delete_id>\d+)/$', views.customer_delete, name="customer_delete"),

    #############################################rbac
    path('rbac/', include("rbac.urls")),
    ##################################车辆分类URL###############################
    # 显示车辆分类列表
    re_path('^car_type/list/$', views.CarTypeView.as_view(), name="car_type_list"),
    # 添加车辆分类URL(CBV形式)
    re_path('^car_type/add/$', views.AddCarTypeView.as_view(), name="car_type_add"),
    # 删除车辆分类URL(CBV形式)
    re_path('^car_type/delete/(?P<car_type_delete_id>\d+)/$', views.car_type_delete, name="car_type_delete"),
    # 编辑车辆分类URL(CBV形式)
    re_path('^car_tyoe/edit/(\d+)/$', views.EditCarTypeView.as_view(), name="car_type_edit"),

    ##################################12元加油站URL###############################
    # 显示12元加油站列表
    re_path('^petrolstation12/list/$', views.Petrolstation12View.as_view(), name="petrolstation12_list"),
    # 添加12元加油站URL(CBV形式)
    re_path('^petrolstation12/add/$', views.AddPetrolstation12View.as_view(), name="petrolstation12_add"),
    # 删除12元加油站URL(CBV形式)
    re_path('^petrolstation12/delete/(?P<petrolstation12_delete_id>\d+)/$', views.petrolstation12_delete,
            name="petrolstation12_delete"),
    # 编辑12元加油站URL(CBV形式)
    re_path('^petrolstation12/edit/(\d+)/$', views.EditPetrolstation12View.as_view(), name="petrolstation12_edit"),

    ##################################30元加油站URL###############################
    # 显示30元加油站列表
    re_path('^petrolstation30/list/$', views.Petrolstation30View.as_view(), name="petrolstation30_list"),
    # 添加30元加油站URL(CBV形式)
    re_path('^petrolstation30/add/$', views.AddPetrolstation30View.as_view(), name="petrolstation30_add"),
    # 删除30元加油站URL(CBV形式)
    re_path('^petrolstation30/delete/(?P<petrolstation30_delete_id>\d+)/$', views.petrolstation30_delete,
            name="petrolstation30_delete"),
    # 编辑30元加油站URL(CBV形式)
    re_path('^petrolstation30/edit/(\d+)/$', views.EditPetrolstation30View.as_view(), name="petrolstation30_edit"),

    ##################################车辆URL###############################
    # 显示车辆信息列表
    re_path('^car/list/$', views.CarView.as_view(), name="car_list"),
    # 添加车辆URL(CBV形式)
    re_path('^car/add/$', views.AddCarView.as_view(), name="car_add"),
    # 删除车辆URL(CBV形式)
    re_path('^car/delete/(?P<car_delete_id>\d+)/$', views.car_delete, name="car_delete"),
    # 编辑车辆URL(CBV形式)
    re_path('^car/edit/(\d+)/$', views.EditCarView.as_view(), name="car_edit"),
    ####################油品URL#####################################
    # 显示油品信息列表
    re_path('^oil/list/$', views.OilView.as_view(), name="oil_list"),
    # 添加油品URL(CBV形式)
    re_path('^oil/add/$', views.AddOilView.as_view(), name="oil_add"),
    # 删除油品URL(CBV形式)
    re_path('^oil/delete/(?P<oil_delete_id>\d+)/$', views.oil_delete, name="oil_delete"),
    # 编辑油品URL(CBV形式)
    re_path('^oil/edit/(\d+)/$', views.EditOilView.as_view(), name="oil_edit"),
    ####################油库URL#####################################
    # 显示油库信息列表
    re_path('^oilwarehouse/list/$', views.OilwarehouseView.as_view(), name="oilwarehouse_list"),
    # 添加油库URL(CBV形式)
    re_path('^oilwarehouse/add/$', views.AddOilwarehouseView.as_view(), name="oilwarehouse_add"),
    # 删除油库URL(CBV形式)
    re_path('^oilwarehouse/delete/(?P<oilwarehouse_delete_id>\d+)/$', views.oilwarehouse_delete,
            name="oilwarehouse_delete"),
    # 编辑油库URL(CBV形式)
    re_path('^oilwarehouse/edit/(\d+)/$', views.EditOilwarehouseView.as_view(), name="oilwarehouse_edit"),
    ####################加油站URL#####################################
    # 显示加油站信息列表
    re_path('^petrolstation/list/$', views.PetrolstationView.as_view(), name="petrolstation_list"),
    # 添加加油站URL(CBV形式)
    path('petrolstation/add/', views.AddPetrolstationView.as_view(), name="petrolstation_add"),
    # 删除加油站URL(CBV形式)
    re_path('^petrolstation/delete/(?P<petrolstation_delete_id>\d+)/$', views.petrolstation_delete,
            name="petrolstation_delete"),
    # 编辑加油站URL(CBV形式)
    re_path('^petrolstation/edit/(\d+)/$', views.EditPetrolstationView.as_view(), name="petrolstation_edit"),

    ####################加油站油库里程设置URL#####################################
    # 显示加油站油库里程信息列表
    re_path('^petrolstation2oilwarehouse/list/$', views.Petrolstation2oilwarehouseView.as_view(),
            name="petrolstation2oilwarehouse_list"),
    # 添加加油站油库里程URL(CBV形式)
    re_path('^petrolstation2oilwarehouse/add/$', views.AddPetrolstation2oilwarehouseView.as_view(),
            name="petrolstation2oilwarehouse_add"),
    # 删除加油站油库里程URL(CBV形式)
    re_path('^petrolstation2oilwarehouse/delete/(?P<petrolstation2oilwarehouse_delete_id>\d+)/$',
            views.petrolstation2oilwarehouse_delete,
            name="petrolstation2oilwarehouse_delete"),
    # 编辑加油站油库里程URL(CBV形式))(这里有个坑,会跳转到oilwarehouse/edit)
    re_path('^petrolstation2oilwarehouse/edit/(\d+)/$', views.EditPetrolstation2oilwarehouseView.as_view(),
            name="petrolstation2oilwarehouse_edit"),

    ####################客户里程价格URL#####################################
    # 显示客户里程价格信息列表
    re_path('^customer2mileage/list/$', views.Customer2mileageView.as_view(),
            name="customer2mileage_list"),
    # 添加客户里程价格URL(CBV形式)
    re_path('^customer2mileage/add/$', views.AddCustomer2mileageView.as_view(),
            name="customer2mileage_add"),
    # 删除客户里程价格URL(CBV形式)
    re_path('^customer2mileage/delete/(?P<customer2mileage_delete_id>\d+)/$',
            views.customer2mileage_delete,
            name="customer2mileage_delete"),
    # 编辑客户里程价格URL(CBV形式)
    re_path('^customer2mileage/edit/(\d+)/$', views.EditCustomer2mileageView.as_view(),
            name="customer2mileage_edit"),

    #############################手机操作#############################
    # 手机登录URL
    re_path('^phone/login/$', views.phone_login, name="phone_login"),
    re_path('^phone/index/$', views.phone_index, name="phone_index"),
    re_path('^phone/information/$', views.phone_information, name="phone_information"),
    re_path('^phone/information_audit/$', views.phone_information_audit, name="phone_information_audit"),
    # path('phone/submit_success/', views.phone_submit_success, name="phone_submit_success"),
    #######################填写信息收集#########################
    re_path('^information/list/$', views.InformationView.as_view(), name="information_list"),
    re_path('^information/edit/(\d+)/$', views.EditInformationView.as_view(), name="information_edit"),
    re_path('^information/delete/(\d+)/$', views.information_delete, name="information_delete"),
    #######################结算运费URL#########################
    re_path('^settlement/list/$', views.SettlementView.as_view(), name="settlement_list"),
    #######################工资结算URL#########################
    # 不去重url
    re_path('^earning/list/$', views.EarningView.as_view(), name="earning_list"),
    re_path('^earning/list/distinct/$', views.EarningDistinctView.as_view(), name="earning_list_distinct"),
    ###############统计报表URL########################
    # 统计今日,昨天,本周,本月下单统计
    re_path('^orderstatistics/$', views.OrderstatisticsView.as_view(), name="orderstatistics"),

    ################工资结算URL######################
    re_path('^information/audit/(\d+)/$', views.information_audit, name="information_audit"),
    # 获取对应客户的收货单位
    re_path('^getpetrolstation/$', views.getpetrolstation, name="getpetrolstation"),
    ###############导出excel#########################
    re_path('^export_imformation/$', views.export_imformation, name="export_imformation"),
    re_path('^export_settlement/$', views.export_settlement, name="export_settlement"),
    re_path('^export_earning/$', views.export_earning, name="export_earning"),
    re_path('^export_earning_distinct/$', views.export_earning_distinct, name="export_earning_distinct"),
    ##########################员工每月工资汇总########################
    re_path('^driver_month_salary/$', views.DriverMonthSalaryView.as_view(), name="driver_month_salary"),
    re_path('^supercargo_month_salary/$', views.SupercargoMonthSalaryView.as_view(), name="supercargo_month_salary"),
    ######################导出员工每月工资url#################################
    re_path('^export_driver_month_salary/$', views.export_driver_month_salary, name="export_driver_month_salary"),
    re_path('^export_supercargo_month_salary/$', views.export_supercargo_month_salary, name="export_supercargo_month_salary"),
    #################员工每月上班天数########################
    re_path('^driver_month_work_days/$', views.driver_month_work_days, name="driver_month_work_days"),
    re_path('^supercargo_month_work_days/$', views.supercargo_month_work_days, name="supercargo_month_work_days"),
    ########################导出员工url#############################
    re_path('^export_supercargo_month_work_days/$', views.export_supercargo_month_work_days, name="export_supercargo_month_work_days"),
    re_path('^export_driver_month_work_days/$', views.export_driver_month_work_days, name="export_driver_month_work_days"),
    re_path('^export_petrolstation/$', views.export_petrolstation, name="export_petrolstation"),
    re_path('^export_petrolstation2oilwarehouse/$', views.export_petrolstation2oilwarehouse, name="export_petrolstation2oilwarehouse"),
    re_path('^export_petrolstation12/$', views.export_petrolstation12, name="export_petrolstation12"),

]
