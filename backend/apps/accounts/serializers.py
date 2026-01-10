"""
Accounts app serializers.
User, Profile, and Manager serializers.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Profile, Manager


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for basic user information.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 
                  'is_active', 'is_verified', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    User creation serializer (for registration).
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role', 
                  'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'default': 'customer'},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """
    Profile serializer with calendar sync fields.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'user_id', 'phone', 'avatar', 'timezone', 'preferences',
                  'calendar_sync_enabled', 'calendar_provider', 'calendar_access_token',
                  'calendar_refresh_token', 'calendar_calendar_id', 'calendar_sync_settings',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'calendar_access_token': {'write_only': True},
            'calendar_refresh_token': {'write_only': True},
        }


class ManagerSerializer(serializers.ModelSerializer):
    """
    Manager serializer with permissions configuration.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    managed_staff = serializers.PrimaryKeyRelatedField(many=True, read_only=True, required=False)
    managed_customers = serializers.PrimaryKeyRelatedField(many=True, read_only=True, required=False)
    
    class Meta:
        model = Manager
        fields = ['id', 'user', 'user_id', 'permissions', 'can_manage_all',
                  'can_manage_customers', 'can_manage_staff', 'can_manage_appointments',
                  'can_view_reports', 'managed_locations', 'managed_staff', 'managed_customers',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ManagerPermissionsSerializer(serializers.Serializer):
    """
    Serializer for updating manager permissions.
    """
    can_manage_all = serializers.BooleanField(required=False)
    can_manage_customers = serializers.BooleanField(required=False)
    can_manage_staff = serializers.BooleanField(required=False)
    can_manage_appointments = serializers.BooleanField(required=False)
    can_view_reports = serializers.BooleanField(required=False)
    managed_locations = serializers.ListField(child=serializers.IntegerField(), required=False)
    permissions = serializers.DictField(required=False)
