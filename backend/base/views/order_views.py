from datetime import datetime

from base.models import Product, Order, OrderItem, ShippingAddress

from base.serializers import OrderSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data
    #print("data",data.get("orderItems"))
    orderItems = data.get('orderItems')
    

    if orderItems and len(orderItems) == 0:
        return Response(
            {"detail": "No Order Items"}, status=status.HTTP_400_BAD_REQUEST
        )
    else:
        # (1)Crate Order

        order = Order.objects.create(
            user=user,
            paymentMethod=data.get('paymentMethod'),
            taxPrice=data.get('taxPrice'),
            shippingPrice=data.get('shippingPrice'),
            totalPrice=data.get('totalPrice'),
        )

        # (2)Create Shipping address
        shippingAddress = data.get('shippingAddress')
        print(type(shippingAddress),'runnintg')
        shipping = ShippingAddress.objects.create(
            order=order,
            address=shippingAddress['address'],
            city=shippingAddress.get('city'),
            postalCode=shippingAddress.get('postalCode'),
            country=shippingAddress.get('country'),
        )
        # (3)Create Order Items and set order to orderItem relationship
        for i in orderItems:
            product = Product.objects.get(_id=i["product"])
            

            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                qty=i["qty"],
                price=i["price"],
                image=product.image.url.removeprefix('/images/'),
            )
           
            # (4)Update stock

            product.countInStock -= int(item.qty)
            product.save()

        # Serialize the order data before returning to frontend

        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user

    # only the admin or the user who made the order can view order
    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "Not authorized to view this order"},
                status=status.HTTP_403_FORBIDDEN,
            )

    except:
        return Response(
            {"detail": "Order Does Not exist"}, status=status.HTTP_404_NOT_FOUND
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request,pk):
    order = Order.objects.get(_id=pk)

    order.isPaid = True
    order.paidAt = datetime.now()
    order.save()
    return Response('order was paid')