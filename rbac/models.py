from django.db import models


# RBAC权限分配
# 用户表
class User(models.Model):
    name = models.CharField(max_length=32)
    pwd = models.CharField(max_length=32)
    roles = models.ManyToManyField("Role")


# 角色表
class Role(models.Model):
    title = models.CharField(max_length=32)
    permissions = models.ManyToManyField("Permission")


# 权限表
class Permission(models.Model):
    title = models.CharField(max_length=32)
    url = models.CharField(max_length=32)
