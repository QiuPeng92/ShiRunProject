from django.shortcuts import render, HttpResponse, redirect


# Create your views here.

def customers(request):
    if request.method == "POST":
        return HttpResponse("添加成功")
    return render(request, "rbac/customers.html")


def orders(request):
    return HttpResponse("orders")
