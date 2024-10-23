from django.contrib import messages,auth
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from . forms import RegisterForm, UserForm, UserProfileForm, UserAddressForm
from . models import Account, UserProfile, Address, Province, City, District
from carts.models import Cart, CartItem
from carts.views import _cart_id
from django.contrib.auth.decorators import login_required

from orders.models import Order, OrderProduct
from store.models import Product, ViewCount

import json

#vertification account
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            firs_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.object.create_user(
                first_name=firs_name, 
                last_name=last_name, 
                email=email, 
                username=username, 
                password=password
                )
            user.phone_number = phone_number
            user.save()

            # Create  user Profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            #user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/vertification/account_vertification_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Registration Succesfuly')
            return redirect('/accounts/login/?command=verification&email=' +email)
    else:
        form = RegisterForm()
    
    context = {
        'form': form
    }
            
    return render(request, 'accounts/registration/register.html', context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active= True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'invalid activation link')
        return redirect('register')

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exits = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exits:
                    cart_item = CartItem.objects.filter(cart=cart)

                    #gatting the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))

                    #Get the cart item from the user to access his product variation
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variantion = item.variation.all()
                        ex_var_list.append(list(existing_variantion))
                        id.append(item.id)

                    # product_variation = [1,2,3,4,6]
                    # ex_var_list = [4,6,3,5]
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity =+ 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save() 

            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            print(user.is_admin)
            
            if user.is_admin == True:
                messages.success(request, 'You are now logged in.')
                return redirect('dashboard_admin')
            
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')           
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login') 

    return render(request, 'accounts/registration/login.html')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.object.filter(email=email).exists():
            user = Account.object.get(email__exact=email)
            #Rsset password emai
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/vertification/reset_password_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sant to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exits')
            return redirect('forgotPassword')

    return render(request, 'accounts/registration/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please Reset your Password ')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')

@login_required(login_url = 'login')
def dashboard(request):
    orders_count = 0
    pending = 0
    confirm = 0
    ontheway = 0
    delivered = 0
    userprofile = get_object_or_404(UserProfile, user=request.user)
    views = Product.objects.filter(users_wislist=request.user)
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    pending= orders.filter(status='PENDING').count()
    confirm= orders.filter(status='CONFIRM').count()
    ontheway= orders.filter(status='ON_THE_WAY').count()
    delivered= orders.filter(status='DELIVERED').count()
    comleted= orders.filter(status='COMMITTED').count() + delivered


    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
        'views': views,
        'pending': pending,
        'confirm': confirm,
        'ontheway': ontheway,
        'delivered': delivered,
        'comleted': comleted,
    }
    return render(request, 'accounts/dashboard.html', context)

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.object.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset Succesfuly')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/profile/resetPassword.html')

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been update')
            return redirect('dashboard')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile
    }
    return render(request, 'accounts/profile/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.object.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.logout(request)
                messages.success(request, 'Password update successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match')
            return redirect('change_password')

    return render(request, 'accounts/profile/change_password.html')

def getCity(request):
    if request.method == "GET":
        province_id = request.GET.get('province_id')
        city_id = list(City.objects.filter(province=province_id).values())
        data = dict()
        data = {
            'data': city_id
        }
    # pass
        return JsonResponse(data)
    
def getDistrict(request):
    if request.method == 'GET':
        city_id = request.GET.get('city_id')
        district_id = list(District.objects.filter(city=city_id).values())
        data = dict()
        data = {
                'data': district_id
            }
        return JsonResponse(data)

@login_required(login_url='login')
def address(request):
    address = Address.objects.filter(user=request.user)

    context = {
        'address': address
    }
    return render(request, 'accounts/delivery/address.html', context)

@login_required(login_url='login')
def add_address(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    prov = Province.objects.all()
    url = request.META.get('HTTP_REFERER')
    

    if request.method == "POST":
        print('Addr :', request.POST)
        address_form = UserAddressForm(data=request.POST or None)
        district_id = request.POST.get('district')
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user_id = request.user.id
            address.district_id = district_id
            address.default = True
            address.save()

            # Update default address
            if address.default:
                Address.objects.filter(user=request.user).exclude(id=address.id).update(default=False)
                address.save()
            else:
                Address.objects.filter(user=request.user, default=True).update(default=False)
                address.save()

            messages.success(request, 'Your address has been created')
            return redirect('address')
        else:
            messages.error(request, 'Your address is not Valid')
        
    else:   
        address_form = UserAddressForm()
            
    context = {
            "prov": prov,
            "form": address_form
        }
    return render(request, 'accounts/delivery/add_address.html', context)

@login_required(login_url='login')
def edit_address(request, id):

    if not request.user.is_authenticated:
        return redirect('login')
    
    prov = Province.objects.all()
    address_get = get_object_or_404(Address, pk=id, user=request.user)

    if not address_get:
        messages.error(request, 'Your address not found')
        return redirect("address")

    try:
        if request.method == 'POST':
            # print('req :', request.POST)
            address = Address.objects.get(id=address_get.id, user=request.user)
            address.first_name = request.POST['first_name']
            address.last_name = request.POST['last_name']
            address.email = request.POST['email']
            address.phone = request.POST['phone']
            address.address_line_1 = request.POST['address_line_1']
            address.address_line_2 = request.POST['address_line_2']
            address.district_id = request.POST['district']
            address.save()

            messages.success(request, 'Your address has been updated')
            return redirect("address")
    except Exception as e:
        print(e)
        messages.error(request, 'Your address incorrect or invalid')
        return redirect("edit_address", id=id)
    
    context = {
            "prov": prov,
            "address": address_get,
        }
    return render(request, 'accounts/delivery/edit_address.html', context)

@login_required(login_url='login')
def delete_address(request, id):
    address = Address.objects.filter(pk=id, user=request.user).delete()
    messages.success(request, 'Your address has been Deleted')
    return redirect("address")

@login_required(login_url="login")
def set_default(request, id):
    Address.objects.filter(user=request.user, default=True).update(default=False)
    Address.objects.filter(pk=id, user=request.user).update(default=True)
    return redirect(request.META["HTTP_REFERER"])

#user_wislist
@login_required
def add_to_wislist(request, id):
    product = get_object_or_404(Product, id=id )
    if product.users_wislist.filter(id=request.user.id).exists():
        product.users_wislist.remove(request.user)
        messages.success(request, 'Remove ' + product.name + 'to your wishlist')
    else:
        product.users_wislist.add(request.user)
        messages.success(request, product.name + ' Has been success from your wishlist')
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required(login_url='login')
def my_wishlists(request):

    product = Product.objects.filter(users_wislist=request.user, productitem__is_default=True)
    
    context = {
        "wishlist": product
    }
    return render(request, 'accounts/my_wishlist.html', context)
