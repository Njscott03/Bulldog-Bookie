# core/serializers.py
from rest_framework import serializers
from core.models import CustomUser, Wager

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'is_admin', 'wallet_balance']
        read_only_fields = ['id', 'is_admin', 'wallet_balance']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class WagerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wager
        fields = ['id', 'user', 'game', 'line', 'amount', 'payout', 'status', 'placed_at', 'settled_at', 'profit']
        read_only_fields = ['id', 'placed_at', 'settled_at', 'profit']
