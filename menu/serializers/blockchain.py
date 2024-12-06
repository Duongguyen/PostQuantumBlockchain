from rest_framework import serializers

from menu.models import TitlePage, New

class TitlePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitlePage
        fields = '__all__'


class NewSerializer(serializers.ModelSerializer):
    class Meta:
        model = New
        fields = '__all__'