import re

from rest_framework import serializers

from apps.user.models.user_model import User


# <<------------------------------------Registration Serializer---------------------------------------->>
class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=30, required=True)
    confirm_password = serializers.CharField(max_length=30, required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(max_length=20, required=True)

    def validate_phone(self, value):
        pattern = r"^\+[1-9]\d{1,14}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("Phone number must be in international format (e.g., +1234567890).")
        return value

    def validate_password(self, value):
        """
        Validate password complexity:
        - Length already enforced by min_length/max_length.
        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one digit.
        - At least one special character.
        """
        # Check for uppercase
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        # Check for lowercase
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        # Check for digit
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        # Check for special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:'\",.<>/?`~"
        if not any(char in special_chars for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, data):
        # Check password match
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Check uniqueness
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError({"username": "A user with this username already exists."})
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        if User.objects.filter(phone=data["phone"]).exists():
            raise serializers.ValidationError({"phone": "A user with this phone number already exists."})

        return data
