"""
项目用到的form类
"""

from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from salary import models


# 校验的顺序:先效验字段的基本属性,再效验局部钩子函数,最后效验全局钩子函数

# 定义一个注册的form类
class RegForm(forms.Form):
    # 用户名
    username = forms.CharField(
        max_length=15,
        label="用户名",
        widget=widgets.TextInput(
            attrs={"class": "form-control", "placeholder": "账号名"},
        ),
        error_messages={
            "max_length": "用户名最长为16位",
            "required": "用户名不能为空!"
        },
    )
    # 密码
    password = forms.CharField(
        min_length=6,
        label="密码",
        widget=widgets.PasswordInput(
            attrs={"class": "form-control", "placeholder": "密码"},
            # 当报错时,保留密码值
            render_value=True,
        ),
        error_messages={
            "min_length": "密码至少6位",
            "required": "密码不能为空!"
        },
    )
    # 确认密码
    re_password = forms.CharField(
        min_length=6,
        label="确认密码",
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control", "placeholder": "确认密码"},
            # 当报错时,保留密码值
            render_value=True,
        ),
        error_messages={
            "min_length": "密码至少6位",
            "required": "确认密码不能为空!"
        },

    )
    # 邮箱
    email = forms.EmailField(
        label="邮箱",
        # 可以为空
        required=False,
        widget=forms.widgets.EmailInput(
            attrs={"class": "form-control", "placeholder": "邮箱"},
        ),
        error_messages={
            "invalid": "邮箱格式不正确!",
            # "required": "邮箱不能为空!",
        }

    )

    # 局部钩子函数
    def clean_username(self):
        # 获取username值(已经通过第一层校验)
        val = self.cleaned_data.get("username")
        # 查询数据库中是否存在
        user_obj = models.UserInfo.objects.filter(username=val).first()
        # 如果存在
        if user_obj:
            raise ValidationError("用户名已经存在!")
        else:
            return val

    # 重写全局的钩子函数,对确认密码做校验
    def clean(self):
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")
        if re_password and re_password != password:
            self.add_error("re_password", ValidationError("两次密码不一致"))
        else:
            return self.cleaned_data


# Userinfo的ModelForm
class UserinfoModelForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ["phone", "username", "password"]
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]
        error_messages = {
            'username': {'required': "用户名不能为空", },
            'password': {'required': "密码不能为空", },
        }

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# Customer的ModelForm
class CustomerModelForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# CarType的ModelForm
class CarTypeModelForm(forms.ModelForm):
    class Meta:
        model = models.CarType
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# Petrolstation12的ModelForm
class Petrolstation12ModelForm(forms.ModelForm):
    class Meta:
        model = models.Petrolstation12
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# Petrolstation30的ModelForm
class Petrolstation30ModelForm(forms.ModelForm):
    class Meta:
        model = models.Petrolstation30
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# Car的ModelForm
class CarModelForm(forms.ModelForm):
    class Meta:
        model = models.Car
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, ModelChoiceField):
                field.widget.attrs.update({'class': 'selectpicker form-control', "data-live-search": "true"})
            else:
                field.widget.attrs.update({'class': 'form-control'})


# Oil的ModelForm
class OilModelForm(forms.ModelForm):
    class Meta:
        model = models.Oil
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# Oilwarehouse的ModelForm
class OilwarehouseModelForm(forms.ModelForm):
    class Meta:
        model = models.Oilwarehouse
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# Petrolstation的ModelForm
class PetrolstationModelForm(forms.ModelForm):
    class Meta:
        model = models.Petrolstation
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, ModelChoiceField):
                field.widget.attrs.update({'class': 'selectpicker form-control', "data-live-search": "true"})
            else:
                field.widget.attrs.update({'class': 'form-control'})


from django.forms.models import ModelChoiceField


# Petrolstation2oilwarehouse的ModelForm
class Petrolstation2oilwarehouseModelForm(forms.ModelForm):
    class Meta:
        model = models.Petrolstation2oilwarehouse
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, ModelChoiceField):
                field.widget.attrs.update({'class': 'selectpicker form-control', "data-live-search": "true"})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    # # 全局钩子函数,使油库和加油站不能重复填写
    # def clean(self):
    #     # 获取油库
    #     oilwarehouse = self.cleaned_data.get("oilwarehouse")
    #     # 获取加油站
    #     petrolstation = self.cleaned_data.get("petrolstation")
    #
    #     petrolstation2oilwarehouse_obj = models.Petrolstation2oilwarehouse.objects.filter(oilwarehouse=oilwarehouse,petrolstation=petrolstation).first()
    #     if petrolstation2oilwarehouse_obj:
    #         # 添加错误
    #         self.add_error("petrolstation", ValidationError("已有该油库和加油站的数据,请勿重新填写!"))
    #     else:
    #         # 放行!
    #         return self.cleaned_data


# Customer2mileage的ModelForm
class Customer2mileageModelForm(forms.ModelForm):
    class Meta:
        model = models.Customer2Mileage
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        # exclude = ["name",]

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, ModelChoiceField):
                field.widget.attrs.update({'class': 'selectpicker form-control', "data-live-search": "true"})
            else:
                field.widget.attrs.update({'class': 'form-control'})


# Information的ModelForm
class InformationModelForm(forms.ModelForm):
    class Meta:
        model = models.Information
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        exclude = ["name", "status_audit", "auditor", "long_price", "short_price",
                   "earning"]
        error_messages = {
            'drive_number': {'required': '车次选项不能为空'},
            'cabin': {'required': '车舱选项不能为空'},
            'customer': {'required': '发货单位选项不能为空'},
            'oilwarehouse': {'required': '发货地址选项不能为空'},
            'petrolstation': {'required': '收货地址选项不能为空'},
            'oil': {'required': '油品选项不能为空'},
            'paid_in_number': {'required': '实收数目不能为空'},
            'car': {'required': '车辆不能为空'},
        }

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, ModelChoiceField):
                field.widget.attrs.update({'class': 'selectpicker form-control', "data-live-search": "true"})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    # 重写全局的钩子函数,对收货单位做效验做校验
    def clean(self):
        # 获取客户名称
        customer_name = self.cleaned_data.get("customer")
        # 获取加油站名称
        petrolstation_name = self.cleaned_data.get("petrolstation")
        # 过滤客户对象
        customer_obj = models.Customer.objects.filter(name=customer_name).first()
        # 过滤加油站对象
        petrolstation_obj = models.Petrolstation.objects.filter(name=petrolstation_name).first()
        # 如果客户的主键值和加油站的customer_id不匹配
        if customer_obj.id != petrolstation_obj.customer_id:
            # 添加错误
            self.add_error("petrolstation", ValidationError("所选加油站与客户不匹配!"))
        else:
            # 放行!
            return self.cleaned_data


# Information的ModelForm
class PhoneInformationModelForm(forms.ModelForm):
    class Meta:
        model = models.Information
        fields = "__all__"
        # 生成form表单的时候,排除哪些字段
        exclude = ["name", "car", "status_audit", "auditor", "long_price", "short_price",
                   "earning", "deliver_time"]
        error_messages = {
            'drive_number': {'required': '车次选项不能为空'},
            'cabin': {'required': '车舱选项不能为空'},
            'customer': {'required': '发货单位选项不能为空'},
            'oilwarehouse': {'required': '发货地址选项不能为空'},
            'petrolstation': {'required': '收货地址选项不能为空'},
            'oil': {'required': '油品选项不能为空'},
            'paid_in_number': {'required': '实收数目不能为空'},
        }

    # 给每个字段添加属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, ModelChoiceField):
                field.widget.attrs.update({'class': 'selectpicker form-control', "data-live-search": "true"})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    # 重写全局的钩子函数,对收货单位做效验做校验
    def clean(self):
        # 获取客户名称
        customer_name = self.cleaned_data.get("customer")
        # 获取加油站名称
        petrolstation_name = self.cleaned_data.get("petrolstation")
        # 过滤客户对象
        customer_obj = models.Customer.objects.filter(name=customer_name).first()
        # 过滤加油站对象
        petrolstation_obj = models.Petrolstation.objects.filter(name=petrolstation_name).first()
        if customer_obj and petrolstation_obj:
            # 如果客户的主键值和加油站的customer_id不匹配
            if customer_obj.id != petrolstation_obj.customer_id:
                # 添加错误
                self.add_error("petrolstation", ValidationError("所选加油站与客户不匹配!"))
        else:
            # 放行!
            return self.cleaned_data
