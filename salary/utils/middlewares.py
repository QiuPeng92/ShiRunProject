from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


# 编写中间件,用户效验用户登录
class LoginMiddleWare(MiddlewareMixin):
    # 在url之前执行
    def process_request(self, request):
        # 添加登录白名单,不需要效验
        if request.path in ["/login/", "register"]:
            return None
        # 如果session中没有登录的记录,就跳转到登录界面
        if not request.user.nid:
            return redirect("/login/")


#路径导航列表
request
