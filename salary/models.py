from django.db import models
from django.contrib.auth.models import AbstractUser
# 多选(不加MultiSelectField,choices只能选一个)
from multiselectfield import MultiSelectField
from django.utils.safestring import mark_safe


# 用户信息表(继承django自带对的Auth表)
class UserInfo(AbstractUser):
    """
    员工表
    """
    # 主键值
    nid = models.AutoField(primary_key=True)
    # 重写邮箱
    email = models.CharField(max_length=32, verbose_name="邮箱", null=True, blank=True)

    # 手机号(null是数据库层面的,blank是提交页面为空)
    phone = models.IntegerField(null=True, blank=True, unique=True, help_text="手机号", verbose_name="手机号")
    # 头像 在upload_to参数中没有/,说明直接在项目的根目录中查找avatar文件夹,如果没有就创建
    avatar = models.FileField(upload_to="avatars/", default="avatars/default.png ", verbose_name="头像")

    # 创建时间(auto_now_add为创建时间,一旦创建就不会改变)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    # # 所属部门(多对一关联)
    # department = models.ForeignKey(to="Department", on_delete=models.CASCADE, default=1,null=True,blank=True)

    # 联合唯一:
    # class Meta:
    #     unique_together = ("name", "department")    #代表name和department不能同时相同

    # 打印UserInfo对象时,就会打印它的username值,__str__必须是字符串
    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "员工信息"
        verbose_name = "员工信息"


# 客户管理表
class Customer(models.Model):
    """
    客户表
    """
    # 客户名称(并且设置为unique,不能重复)
    name = models.CharField(max_length=32, unique=True, verbose_name="姓名")
    # 备注(help_text在admin中显示,verbose_name也在admin中显示),null=True限制数据库可以为空,blank=True限制输入可以为空
    remark = models.TextField(max_length=32, null=True, blank=True, help_text="备注", verbose_name="备注")

    # 打印对象时，将打印__str__,__str__必须是字符串
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "客户信息"
        verbose_name_plural = "客户信息"


# 车辆管理表
class Car(models.Model):
    """
    车辆管理表
    """
    # 车牌号码
    name = models.CharField(max_length=32, unique=True, verbose_name="车牌号码")
    # 驾驶员
    driver = models.ForeignKey(to="UserInfo", on_delete=models.CASCADE, related_name="car_drivers", verbose_name="驾驶员")
    # 押运员
    supercargo = models.ForeignKey(to="UserInfo", on_delete=models.CASCADE, related_name="car_supercargos",
                                   verbose_name="押运员")
    # 车型
    car_type = models.ForeignKey(to="CarType", on_delete=models.CASCADE, related_name="car_type", verbose_name="车型")
    # 备注
    remark = models.CharField(max_length=32, null=True, blank=True, verbose_name="备注")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "车辆信息"
        verbose_name_plural = "车辆信息"


# 车辆分类表
class CarType(models.Model):
    '''
    车型表
    '''
    # 名称
    name = models.CharField(max_length=32, verbose_name="分类名称", unique=True)
    # 备注
    remark = models.CharField(max_length=32, verbose_name="备注", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "车型"
        verbose_name_plural = "车型"


# 油品管理表
class Oil(models.Model):
    """
    油品管理表
    """
    # 油品名称
    name = models.CharField(max_length=32, unique=True, verbose_name="油品名称")
    # 备注
    remark = models.CharField(max_length=32, null=True, blank=True, verbose_name="备注")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "油品信息"
        verbose_name_plural = "油品信息"


# 油库管理表
class Oilwarehouse(models.Model):
    """
    油库管理表
    """
    # 油库名称
    name = models.CharField(max_length=32, unique=True, verbose_name="油库名称")
    # 备注
    remark = models.CharField(max_length=32, null=True, blank=True, verbose_name="备注")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "油库信息"
        verbose_name_plural = "油库信息"


# 加油站管理表
class Petrolstation(models.Model):
    """
    加油站管理表
    """
    # 加油站名称
    name = models.CharField(max_length=32, unique=True, verbose_name="加油站")
    # 加油站编号
    number = models.CharField(max_length=32, unique=True, verbose_name="加油站编号", null=True, blank=True)
    # 加油站客户
    customer = models.ForeignKey(to="Customer", on_delete=models.CASCADE, verbose_name="客户")
    # 备注
    remark = models.CharField(max_length=32, null=True, blank=True, verbose_name="备注")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "加油站信息"
        verbose_name_plural = "加油站信息"


# 加油站油库里程设置表
class Petrolstation2oilwarehouse(models.Model):
    # 油库
    oilwarehouse = models.ForeignKey(to="Oilwarehouse", on_delete=models.CASCADE, verbose_name="油库")
    # 加油站
    petrolstation = models.ForeignKey(to="Petrolstation", on_delete=models.CASCADE, verbose_name="加油站")
    # 员工里程
    mileage = models.IntegerField(verbose_name="员工里程")
    # 客户里程
    customer_mileage = models.IntegerField(verbose_name="客户里程")
    # 备注
    remark = models.CharField(max_length=120, null=True, blank=True, verbose_name="备注")

    def __str__(self):
        return self.petrolstation.name + self.oilwarehouse.name

    class Meta:
        # 设置这两个字段联合约束
        unique_together = (("petrolstation", "oilwarehouse"),)
        verbose_name = "加油站油库里程设置"
        verbose_name_plural = "加油站油库里程设置"


# 客户里程价格表
class Customer2Mileage(models.Model):
    # 客户名称
    customer = models.OneToOneField(to="Customer", null=True, on_delete=models.CASCADE, verbose_name="客户",
                                    related_name="customer_mileage")
    # 短程标准（公里）
    shortmileage_standard = models.IntegerField(verbose_name="短程标准(公里)")
    # 短程单价(每吨)
    shortmileage_price = models.FloatField(verbose_name="短程单价(每吨)")
    # 长途单价（每吨*公里）
    longmileage_price = models.FloatField(verbose_name="长途单价（每吨*公里）")
    # 生效日期
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # 备注
    remark = models.CharField(max_length=120, null=True, blank=True, verbose_name="备注")

    def __str__(self):
        return self.customer.name

    class Meta:
        verbose_name = "客户里程价格信息"
        verbose_name_plural = "客户里程价格信息"


# 审批状态
status_choices = ((1, '未审批'), (2, '已审批'))
# 车仓选择
cabin_choices = ((1, '第一仓'), (2, '第二仓'), (3, '第三仓'), (4, '第四仓'))
# 车次
drive_number_choices = ((1, '第一车'), (2, '第二车'), (3, '第三车'), (4, '第四车'))


# 员工填写信息表
class Information(models.Model):
    # 发货单位
    customer = models.ForeignKey(to="Customer", on_delete=models.CASCADE, verbose_name="发货单位")
    # 发货地址
    oilwarehouse = models.ForeignKey(to="Oilwarehouse", on_delete=models.CASCADE, verbose_name="发货地址")
    # 收货单位
    petrolstation = models.ForeignKey(to="Petrolstation", on_delete=models.CASCADE, verbose_name="收货单位")
    # 内部单号
    inside_number = models.CharField(max_length=32, null=True, blank=True, verbose_name="内部单号")
    # 外部单号
    outside_number = models.CharField(max_length=32, null=True, blank=True, verbose_name="外部单号")
    # 车次
    drive_number = models.IntegerField(choices=drive_number_choices, verbose_name="车次")
    # 支付金额
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="支付金额")
    # 车辆信息
    car = models.ForeignKey(to="Car", on_delete=models.CASCADE, related_name="car_infocollection", verbose_name="车辆信息")
    # 配送时间
    deliver_time = models.DateField(verbose_name="配送时间")
    # 车舱编号
    cabin = models.IntegerField(choices=cabin_choices, verbose_name="车舱编号")
    # 油品
    oil = models.ForeignKey(to="Oil", on_delete=models.CASCADE, verbose_name="油品")
    # 实收数
    paid_in_number = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="实发数")
    # 审核状态
    status_audit = models.IntegerField(choices=status_choices, default=1, verbose_name="审核状态")
    # 审核人
    auditor = models.CharField(max_length=32, verbose_name="审核人")
    # 短途运费
    short_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    # 长途运费
    long_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    # 工资结算
    earning = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    # 灌桶数
    oiltank_number = models.IntegerField(default=0, verbose_name="灌桶数")
    # 备注
    remark = models.CharField(max_length=32, verbose_name="备注", null=True, blank=True)

    def __str__(self):
        return str(self.car.name) + str(self.customer.name) + str(self.petrolstation.name)

    def get_status(self):
        status_color = {
            1: "red",
            2: "green",
        }
        return mark_safe("<span style='background-color:%s;color:white'>%s</span>" % (
            status_color[self.status_audit], self.get_status_audit_display()))

    class Meta:
        verbose_name = "填写信息表"
        verbose_name_plural = "填写信息表"
        unique_together = (("deliver_time", "cabin", "drive_number", "car"),)


# 新建员工填写信息表(审批后的运费结算和工资结算依据表)
class StaticInformation(models.Model):
    # 内部单号
    inside_number = models.CharField(max_length=32, null=True, blank=True, verbose_name="内部单号")
    # 外部单号
    outside_number = models.CharField(max_length=32, null=True, blank=True, verbose_name="外部单号")
    # 发货单位
    customer_name = models.CharField(max_length=32, verbose_name="发货单位")
    # 配送时间
    deliver_time = models.DateField(verbose_name="配送时间")
    # 车号
    car_name = models.CharField(max_length=32, verbose_name="车号")
    # 车型
    car_type = models.CharField(max_length=32, verbose_name="车型")
    # 驾驶员
    driver = models.CharField(max_length=32, verbose_name="驾驶员")
    # 押运员
    supercargo = models.CharField(max_length=32, verbose_name="押运员")
    # 发货地址
    oilwarehouse = models.CharField(max_length=32, verbose_name="发货地址")
    # 收货单位
    petrolstation = models.CharField(max_length=32, verbose_name="收货单位")
    # 油品
    oil = models.CharField(max_length=32, verbose_name="油品")
    # 车次
    drive_number = models.IntegerField(verbose_name="车次")
    # 车舱编号
    cabin = models.IntegerField(verbose_name="车舱编号")
    # 支付金额
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="支付金额")
    # 实发数
    paid_in_number = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="实收数")
    # 运距
    mileage = models.IntegerField(verbose_name="员工运距")
    # 客户运距
    customer_mileage = models.IntegerField(verbose_name="客户运距")
    # 短程标准（公里）
    shortmileage_standard = models.IntegerField(verbose_name="短程标准(公里)", default=0)
    # 短程单价(每吨)
    shortmileage_price = models.FloatField(verbose_name="短程单价(每吨)", default=0)
    # 长途单价（每吨*公里）
    longmileage_price = models.FloatField(verbose_name="长途单价（每吨*公里）", default=0)
    # 短途运费
    short_price = models.DecimalField(verbose_name="短途运费", max_digits=10, decimal_places=2, null=True, blank=True,
                                      default=0)
    # 长途运费
    long_price = models.DecimalField(verbose_name="长途运费", max_digits=10, decimal_places=2, null=True, blank=True,
                                     default=0)
    # 工资结算
    earning = models.DecimalField(verbose_name="工资结算", max_digits=10, decimal_places=2, null=True, blank=True,
                                  default=0)
    # 油罐数
    oiltank_number = models.IntegerField(default=0, verbose_name="油罐数")
    # 备注
    remark = models.CharField(max_length=32, verbose_name="备注", null=True, blank=True)

    class Meta:
        verbose_name = "通过审核表"
        verbose_name_plural = "通过审核表"


# 12元补贴加油站表
class Petrolstation12(models.Model):
    # 加油站名称
    name = models.CharField(max_length=32, verbose_name="加油站名称", unique=True)
    # 备注
    remark = models.CharField(max_length=32, verbose_name="备注", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "12元加油站表"
        verbose_name = "12元加油站表"


# 30元补贴加油站表
class Petrolstation30(models.Model):
    # 加油站名称
    name = models.CharField(max_length=32, verbose_name="加油站名称", unique=True)
    # 备注
    remark = models.CharField(max_length=32, verbose_name="备注", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "30元加油站表"
        verbose_name = "30元加油站表"


# 员工每月工资汇总表
class MonthSalary(models.Model):
    # 驾驶员名称
    driver_name = models.CharField(max_length=32, verbose_name="驾驶员名称")
    # 押运员名称
    supercargo_name = models.CharField(max_length=32, verbose_name="押运员名称")
    # 驾驶员工资
    driver_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    # 押运员工资
    supercargo_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    # 日期
    deliver_time = models.DateField(verbose_name="配送时间")
    # 车号
    car_name = models.CharField(max_length=32, verbose_name="车号")
    # 车次
    drive_number = models.IntegerField(verbose_name="车次", default=1)

    def __str__(self):
        return "员工每月工资汇总表"

    class Meta:
        verbose_name = "员工每月工资汇总表"
        verbose_name_plural = "员工每月工资汇总表"
