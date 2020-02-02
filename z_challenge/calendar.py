# -*- coding: utf-8 -*-

from django.shortcuts import render

from app import consts
from app import auth
from app.auth import get_default_context, auth_by_vk


def calendar(request):
    """
    Main page
    """

    # if we get 'code' from vk authorization - we generate sid for this user
    sid = None
    vk_code = request.GET.get('code')
    if vk_code:
        sid = auth_by_vk(vk_code) or None

    user = auth.MyUser(request, sid=sid)
    context = get_default_context(request, user=user)
    add_calendar_context(context, user)

    # send sid to HTML, then set cookies with JS
    context['SET_COOKIE_TOKEN'] = sid

    return render(
        request,
        'app/calendar/main.html',
        context
    )


def calendar_user(request, member_id=None):
    """
    User page

    Args:
        member_id: int, user id
    """

    user = auth.MyUser(request)
    context = get_default_context(request, user=user)
    add_calendar_context(context, user)

    if member_id:
        context['CALENDAR_MEMBER_ID'] = member_id

    return render(
        request,
        'app/calendar/main.html',
        context
    )


def calendar_challenge(request, challenge_id=None):
    """
    Challenge page

    Args:
        challenge_id: int, chelenge id
    """

    user = auth.MyUser(request)
    context = get_default_context(request, user=user)
    add_calendar_context(context, user)

    if challenge_id:
        context['CALENDAR_CHALLENGE_ID'] = challenge_id

    return render(
        request,
        'app/calendar/main.html',
        context
    )


def add_calendar_context(context, user):
    """
    Set common context values

    Args:
        context: dict, context values for sending to HTML
        user: MyUser, user object
    """

    context['USER_NAME'] = user.get_user_name() or consts.GUEST
    context['VK_PHOTO'] = user.vk_photo
    context['VK_APP_ID'] = consts.VK_APP_ID
