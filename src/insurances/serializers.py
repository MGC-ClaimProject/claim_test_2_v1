from insurances.models import Insurance
from rest_framework import serializers


class InsuranceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = Insurance
        fields = "__all__"
        read_only_fields = ("id",)
