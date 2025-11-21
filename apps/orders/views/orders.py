import json

from django.views import View
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404

from ..models import Order, OrderItem
from apps.accounts.models import User
from apps.products.models import Product


class OrderListView(View):

    def get(self, request: HttpRequest) -> JsonResponse:
        # if admin -> all
        # if user -> own orders
        orders = [o.to_dict() for o in Order.objects.all()]

        return JsonResponse({'orders': orders})

    def post(self, request: HttpRequest) -> JsonResponse:
        data = json.loads(request.body) if request.body else {}

        {
            "customer": 1,
            "shipping_address": "123 Main St",
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 5, "quantity": 1}
            ]
        }

        customer = data.get('customer')
        if customer:
            user = get_object_or_404(User, pk=customer)
        else:
            return JsonResponse({'customer': 'Required.'}, status=400)
        
        shipping_address = data.get('shipping_address')
        if not shipping_address:
            return JsonResponse({'shipping_address': 'Required.'}, status=400)
        
        items = data.get('items')
        if not items:
            return JsonResponse({'items': 'Required.'}, status=400)
        
        order = Order(
            user=user,
            address=shipping_address
        )

        total = 0
        order_items = []
        for item in items:
            product = get_object_or_404(Product, pk=item['product_id'])
            if product.stock >= item['quantity']:
                total += product.price * item['quantity']
            else:
                return JsonResponse({'item':  'Not enough.'}, status=400)

            order_item = OrderItem(
                order=order,
                product=product,
                quantity=item['quantity'],
                total=product.price * item['quantity']
            )
            order_items.append(order_item)
    
        order.total_price = total
        order.save()

        for item in order_items:
            item.save()

        return JsonResponse(order.to_dict())


class OrderDetailView(View):

    def get(self, request: HttpRequest, pk: int) -> JsonResponse:
        order = get_object_or_404(Order, pk=pk)
        return JsonResponse(order.to_dict())
        

    def put(self, request: HttpRequest, pk: int) -> JsonResponse:
        data = json.loads(request.body) if request.body else {}
        order = get_object_or_404(Order, pk=pk)

        shipping_address = data.get('shipping_address')
        if shipping_address:
            order.address = shipping_address
        
        
        status = data.get('status')
        if status:
            order.status = status
    
        payment_status = data.get('payment_status')
        if payment_status:
            order.payment_status = payment_status

        order.save()
        return JsonResponse(order.to_dict())
    
    def delete(self, request: HttpRequest, pk:int) -> JsonResponse:
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return JsonResponse({'status':'deleted'}, status=204)
