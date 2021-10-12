from django.utils.translation import get_language
from .models import *


def menu_links(request):
    #catg = Category.objects.all().exclude(parent=None).order_by('-created_at')[:7]
    #links = Category.objects.filter(parent=None)
    footcategories = Category.objects.filter(parent=None)[:4]
    catg_parent = Category.objects.filter(parent=None)
    #latest_catg = Category.objects.order_by("-id")[3:10]
    return dict(footcategories=footcategories, catg_parent=catg_parent)

def home_page(request):
    testimonials = Testimonial.objects.all()[:3]
    return dict(testimonials=testimonials)

# def cart_total(request):
#     if request.user.is_authenticated:
#         totalcarts = Cart.objects.filter(user=request.user, purchase=False)
#         return dict(totalcarts=totalcarts)
#     else:
#         totalcarts=[]
#         return totalcarts
