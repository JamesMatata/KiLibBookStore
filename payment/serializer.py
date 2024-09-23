from rest_framework import serializers

from orders.models import Order
from payment.models import LNMOnline


class LNMOnlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = LNMOnline
        fields = "__all__"


class ordersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
