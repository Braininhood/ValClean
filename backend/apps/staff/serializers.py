"""
Staff app serializers.
Staff, StaffSchedule, StaffService, and StaffArea serializers.
"""
from rest_framework import serializers
from .models import Staff, StaffSchedule, StaffService, StaffArea
from apps.services.serializers import ServiceListSerializer


class StaffAreaSerializer(serializers.ModelSerializer):
    """
    Staff service area serializer (postcode + radius; optional service for per-service area).
    """
    service_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    service_name = serializers.CharField(source='service.name', read_only=True, allow_null=True)

    class Meta:
        model = StaffArea
        fields = ['id', 'staff', 'service', 'service_id', 'service_name', 'postcode', 'radius_miles', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'staff', 'created_at', 'updated_at']

    def create(self, validated_data):
        service_id = validated_data.pop('service_id', None)
        from apps.services.models import Service
        validated_data['service'] = Service.objects.get(id=service_id) if service_id else None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        service_id = validated_data.pop('service_id', None)
        if 'service_id' in self.initial_data:
            from apps.services.models import Service
            instance.service = Service.objects.get(id=service_id) if service_id else None
        return super().update(instance, validated_data)


class StaffScheduleSerializer(serializers.ModelSerializer):
    """
    Staff schedule serializer.
    """
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = StaffSchedule
        fields = ['id', 'staff', 'day_of_week', 'day_name', 'start_time', 'end_time',
                  'breaks', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffServiceSerializer(serializers.ModelSerializer):
    """
    Staff-Service relationship serializer with price/duration overrides.
    """
    service = ServiceListSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True, required=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = StaffService
        fields = ['id', 'staff', 'service', 'service_id', 'service_name',
                  'price_override', 'duration_override', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffSerializer(serializers.ModelSerializer):
    """
    Staff serializer with related schedules, services, and areas.
    """
    schedules = StaffScheduleSerializer(many=True, read_only=True)
    services = StaffServiceSerializer(many=True, read_only=True, source='staff_services')
    service_areas = StaffAreaSerializer(many=True, read_only=True, source='service_areas')
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    
    class Meta:
        model = Staff
        fields = ['id', 'user', 'user_email', 'name', 'email', 'phone', 'photo', 'bio',
                  'services', 'schedules', 'service_areas', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StaffListSerializer(serializers.ModelSerializer):
    """
    Simplified staff serializer for public list views (filtered by postcode/area).
    """
    service_areas = serializers.SerializerMethodField()
    
    class Meta:
        model = Staff
        fields = ['id', 'name', 'email', 'phone', 'photo', 'bio', 'service_areas', 'is_active']
    
    def get_service_areas(self, obj):
        """Return active service areas for this staff member."""
        areas = obj.service_areas.filter(is_active=True)
        return [{'postcode': area.postcode, 'radius_miles': float(area.radius_miles)} 
                for area in areas]
