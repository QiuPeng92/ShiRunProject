from django.contrib import admin
from salary.models import *


# Admin的配置类
class InformationConfig(admin.ModelAdmin):
    # 在Admin中显示的字段
    list_display = ["pk", "customer", "oilwarehouse", "petrolstation", "drive_number", "car", "deliver_time", "cabin",
                    "oil", "paid_in_number", "status_audit", "auditor", "short_price", "long_price", "earning",
                    "remark"]
    search_fields = ["deliver_time", "customer__name", "petrolstation__name", "oilwarehouse__name"]
    # 排序方式
    ordering = ["pk"]


class StaticInformationConfig(admin.ModelAdmin):
    list_display = ["customer_name", "deliver_time", "car_name", "car_type", "driver", "supercargo", "oilwarehouse",
                    "petrolstation", "oil", 'drive_number', "cabin", "paid_in_number", "mileage", "customer_mileage",
                    "shortmileage_standard", "short_price", "long_price", "oiltank_number"]
    ordering = ["-deliver_time"]
    search_fields = ["customer_name", "deliver_time", "car_name", "car_type", "driver", "supercargo", "oilwarehouse",
                     "petrolstation"]


admin.site.register(Information, InformationConfig)
admin.site.register(StaticInformation, StaticInformationConfig)
