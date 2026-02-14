from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from .models import Product, Category, Order, OrderItem
from .forms import CheckoutForm
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Q

# 1. HOME VIEW
def home(request):
    query = request.GET.get('search')
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort')

    products_list = Product.objects.all()

    if query:
        products_list = products_list.filter(name__icontains=query)
    if category_id:
        products_list = products_list.filter(category_id=category_id)

    if sort_by == 'price_low':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_high':
        products_list = products_list.order_by('-price')

    paginator = Paginator(products_list, 8)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    categories = Category.objects.all()

    cart_count = 0
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, complete=False).first()
        if order:
            cart_count = order.get_cart_count

    context = {
        'products': products,
        'categories': categories,
        'cart_count': cart_count
    }
    return render(request, 'store/home.html', context)

# 2. CART VIEW
@login_required
def cart(request):
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    items = order.items.all()
    return render(request, 'store/cart.html', {'items': items, 'order': order})

# 3. ADD TO CART
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1

    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    order_item.quantity += quantity
    order_item.save()

    messages.success(request, f"{quantity} x {product.name} added to cart!")
    return redirect('home')

# 4. REMOVE FROM CART
@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order = Order.objects.filter(user=request.user, complete=False).first()
    if order:
        order_item = OrderItem.objects.filter(order=order, product=product).first()
        if order_item:
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
    return redirect('cart')

# 5. CHECKOUT VIEW
@login_required
def checkout(request):
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    items = order.items.all()
    form = CheckoutForm()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    for item in items:
                        if item.product.stock >= item.quantity:
                            item.product.stock -= item.quantity
                            item.product.save()
                        else:
                            raise Exception(f"Sorry, {item.product.name} is out of stock.")

                    order.complete = True
                    order.save()

                    messages.success(request, "Order placed successfully!")
                    return redirect('order_success')

            except Exception as e:
                messages.error(request, str(e))
                return redirect('cart')

    return render(request, 'store/checkout.html', {'form': form, 'items': items, 'order': order})

# 6. AUTH & DETAILS
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def buy_now(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    order_item.quantity += 1
    order_item.save()
    return redirect('cart')

@login_required
def order_history(request):
    # Get all orders for the user
    orders = Order.objects.filter(user=request.user, complete=True).order_by('-date_ordered')

    # Get the search query from the URL
    query = request.GET.get('order_search')

    if query:
        # Filter by Order ID OR by Product Name within the order
        orders = orders.filter(
            Q(id__icontains=query) |
            Q(items__product__name__icontains=query)
        ).distinct()

    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def order_success(request):
    try:
        order = Order.objects.filter(user=request.user, complete=True).latest('date_ordered')
    except Order.DoesNotExist:
        return redirect('home')
    return render(request, 'store/order_success.html', {'order': order})

@login_required
def download_pdf_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    template = get_template('store/pdf_receipt.html')
    context = {'order': order}
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Receipt_Order_{order.id}.pdf"'
        return response

    return HttpResponse("Error generating PDF", status=400)