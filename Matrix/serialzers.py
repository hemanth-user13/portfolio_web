from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password


class UserDetailsSerialzers(serializers.ModelSerializer):
    # profile_image = serializers.ImageField(
    #     required=False,
    #     allow_null=True,
    #     use_url=True 
    # )
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = UserDetails
        fields = [
            "id", "salutation", "title", "first_name", "last_name",
            "email", "password", "confirm_password",
            "created_at", "profile_image","is_admin"
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            'password': {'write_only': True, "required": False}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        action = self.context.get('action')
        if action == "create":
            self.fields["password"].required = True
            self.fields["confirm_password"].required = True
        else:
            self.fields["password"].required = False
            self.fields["confirm_password"].required = False

    def validate(self, data):
        action = self.context.get("action")
        if action == "create":
            if data.get('password') != data.get('confirm_password'):
                raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("confirm_password", None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)

class SalutationsSerailzer(serializers.ModelSerializer):
    class Meta:
        model=Salutations
        fields=["id","name"]

class TitleSerialzer(serializers.ModelSerializer):
    class Meta:
        model=Titles
        fields=["id","name"]

class RatingSerializer(serializers.Serializer):
    rate = serializers.FloatField()
    count = serializers.IntegerField()

class FakeProductDataSerailzer(serializers.ModelSerializer):
    # store rating as dict inside JSONField
    rating = RatingSerializer()

    class Meta:
        model = FakeProductsData
        fields = ["id", "title", "price", "description", "category", "image", "rating"]

    def create(self, validated_data):
        rating_data = validated_data.pop("rating", {})
        validated_data["rating"] = rating_data  # put back dict into JSONField
        return FakeProductsData.objects.create(**validated_data)


class MovieSerialzer(serializers.ModelSerializer):
    class Meta:
        model=Movies
        fields="__all__"
    
class ProductsSerilazers(serializers.ModelSerializer):
    class Meta:
        model=Products
        fields="__all__"


class PartnerSerailzer(serializers.ModelSerializer):
    class Meta:
        model = Partners
        fields = ["id", "name", "address", "zip_code", "mobile_number", "created_user_id","is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["zip_code"].required = True
        self.fields["mobile_number"].required = True
        self.fields["created_user_id"].required = True
        self.fields["address"].required = False
        self.fields["is_active"].required = False