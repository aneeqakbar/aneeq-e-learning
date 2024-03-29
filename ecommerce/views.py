import json
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render,get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from courses.models import Course
from courses.custom_perms import hasEnrolled
from .models import Order, OrderItem, Promocode
from .forms import CouponForm
import datetime

# Create your views here.


def CartView(request):
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    context = {'order':order}
    return render(request, 'ecommerce/cart.html', context)


def CheckoutView(request):
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    context = {'order':order}
    return render(request, 'ecommerce/checkout.html', context)


class UpdateItemAPI(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        course_id = request.POST.get('course_id')
        action = request.POST.get('action')
        user = request.user
        course = Course.objects.get(id=course_id)
        if course in user.profile.enrolled.all():
            return Response(status=status.HTTP_302_FOUND)

        order, created = Order.objects.get_or_create(user=user, complete=False)

        orderItem, created = OrderItem.objects.get_or_create(order=order, referring_course=course)

        if action == 'add':
            orderItem.save()
        elif action == 'remove':
            orderItem.delete()

        return Response(status=status.HTTP_202_ACCEPTED)

class ProceedCheckoutAPI(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        # TODO: Do payment process here
        messages.success(request, "Payment Succeeded!")

        user = request.user
        order = Order.objects.get(user=user, complete=False)

        for item in order.items.all():
            user.profile.enrolled.add(item.referring_course)

        order.complete = True
        order.save()


        return Response(status=status.HTTP_200_OK)


def get_coupon(request, code):
    try:
        promo = Promocode.objects.get(code=code, active=True)
        current_timestamp = datetime.datetime.now().timestamp()
        if promo.valid_from.timestamp() < current_timestamp and promo.valid_to.timestamp() > current_timestamp:
            return promo
        else:
            messages.error(request, 'This Promocode is Expired')
            return None
    except ObjectDoesNotExist:
        messages.error(request, 'This promocode does not exist')
        return None

class AddCouponAPI(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        if request.method == 'POST':
            form = CouponForm(request.POST or None)
            if form.is_valid():
                try:
                    code = form.cleaned_data.get('code')
                    orders = Order.objects.get(user=request.user, complete=False)
                    coupon = get_coupon(request, code)
                    if coupon:
                        orders.coupon = coupon
                        orders.save()
                        messages.success(request, "Successfully Promocode is Added !!")
                        return Response(status=status.HTTP_200_OK)
                    return Response('Invalid Coupon',status=status.HTTP_406_NOT_ACCEPTABLE)
                except ObjectDoesNotExist:
                    messages.info(request, 'You do not have an active order')
                    return Response('Cart Empty', status=status.HTTP_204_NO_CONTENT)
            return Response('Invalid Input', status=status.HTTP_406_NOT_ACCEPTABLE)
