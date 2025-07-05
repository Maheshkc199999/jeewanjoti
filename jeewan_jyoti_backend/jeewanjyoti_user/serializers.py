from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLES, required=True)  # Role selection

    class Meta:
        model = User
        fields = [
            'email', 'password', 'confirm_password', 'role', 
            'birthdate', 'first_name', 'last_name', 'gender', 
            'height', 'weight', 'blood_group', 'profile_image', 
            'specialization', 'license_number', 'hospital_name', 'experience','education','description','phone_number','id'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        role = attrs.get("role")

        if role == "DOCTOR":
            required_fields = ['specialization', 'license_number', 'hospital_name', 'experience','description','phone_number']
        elif role == "NURSE":
            required_fields = ['license_number', 'hospital_name', 'experience','description','phone_number']
        else:  # Role is USER
            required_fields = ['height', 'weight', 'blood_group']

        for field in required_fields:
            if not attrs.get(field):
                raise serializers.ValidationError({field: f"{field} is required for role {role}"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['email', 'password']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'birthdate', 'gender', 'height', 'weight', 'blood_group',
            'first_name', 'last_name'
        ]
        extra_kwargs = {
            'birthdate': {'required': False},
            'gender': {'required': False},
            'height': {'required': False},
            'weight': {'required': False},
            'blood_group': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']


