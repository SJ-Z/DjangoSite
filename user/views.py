import string
import random
import time
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail

from user.forms import LoginForm, RegisterForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from user.models import Profile


def login_for_modal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data.get('user')
        auth.login(request, user)
        data['status'] = 'success'
    else:
        data['status'] = 'error'
    return JsonResponse(data)


def login(request):
    """username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(request, username=username, password=password)
    # 发送此请求的网站
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    if user is not None:
        auth.login(request, user)
        # 跳转到首页
        return redirect(referer)
    else:
        return render(request, 'error.html', {'message': '用户名或密码不正确', 'redirect_to': referer})"""

    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data.get('user')
            auth.login(request, user)
            # 跳转到来源页
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()

    context = {
        'login_form': login_form
    }
    return render(request, 'user/login.html', context)


def register(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST, request=request)
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            email = register_form.cleaned_data.get('email')
            password = register_form.cleaned_data.get('password')
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 清除session
            del request.session['register_code']
            # 登录用户
            user = auth.authenticate(request, username=username, password=password)
            auth.login(request, user)
            # 跳转到来源页
            return redirect(request.GET.get('from', reverse('home')))
    else:
        register_form = RegisterForm()

    context = {
        'register_form': register_form
    }
    return render(request, 'user/register.html', context)


def logout(request):
    auth.logout(request)
    # 跳转到来源页
    return redirect(request.GET.get('from', reverse('home')))


def user_info(request):
    return render(request, 'user/user_info.html')


def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data.get('nickname_new')
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {
        'page_title': '修改昵称',
        'form_title': '修改昵称',
        'submit_text': '修改',
        'form': form,
        'return_back_url': redirect_to
    }
    return render(request, 'form.html', context)


def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            request.user.email = email
            request.user.save()
            # 清除session
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = {
        'page_title': '绑定邮箱',
        'form_title': '绑定邮箱',
        'submit_text': '绑定',
        'form': form,
        'return_back_url': redirect_to
    }
    return render(request, 'user/bind_email.html', context)


def send_verification_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        request.session['bind_email_code'] = code
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'error'
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now

            # 发送邮件
            mail.send_mail('绑定邮箱', '验证码： %s' % code, 'sj17830918173@163.com', [email], fail_silently=False)
            data['status'] = 'success'
    else:
        data['status'] = 'error'
    return JsonResponse(data)


def change_password(request):
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            # 修改密码成功，登出系统
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {
        'page_title': '修改密码',
        'form_title': '修改密码',
        'submit_text': '修改',
        'form': form,
        'return_back_url': redirect_to
    }
    return render(request, 'form.html', context)


def forgot_password(request):
    redirect_to = reverse('login')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            new_password = form.cleaned_data.get('new_password')
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除session
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {
        'page_title': '重置密码',
        'form_title': '重置密码',
        'submit_text': '重置',
        'form': form,
        'return_back_url': redirect_to
    }
    return render(request, 'user/forgot_password.html', context)
