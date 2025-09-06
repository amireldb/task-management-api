from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Task
from django.utils import timezone


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model with all fields and custom validation
    """
    # Read-only field to show username instead of user ID
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'username', 'title', 'description',
            'status', 'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_due_date(self, value):
        """
        Validate that due_date is not in the past for new tasks
        """
        if value and not self.instance:  # Only validate for new tasks
            if value < timezone.now():
                raise serializers.ValidationError(
                    "Due date cannot be in the past."
                )
        return value
    
    def validate_title(self, value):
        """
        Validate that title is not empty or just whitespace
        """
        if not value.strip():
            raise serializers.ValidationError(
                "Title cannot be empty or contain only whitespace."
            )
        return value.strip()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User registration with password confirmation
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Enter the same password for confirmation'
    )
    email = serializers.EmailField(
        required=True,
        help_text='A valid email address'
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name']
        read_only_fields = ['id']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate_email(self, value):
        """
        Check that the email is unique
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value.lower()  # Store emails in lowercase
    
    def validate_username(self, value):
        """
        Validate username format and uniqueness
        """
        if not value.isalnum() and '_' not in value:
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )
        return value
    
    def validate(self, data):
        """
        Check that the passwords match
        """
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        return data
    
    def create(self, validated_data):
        """
        Create a new user with encrypted password
        """
        # Remove password_confirm from validated data
        validated_data.pop('password_confirm', None)
        
        # Create user with encrypted password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Create authentication token for the user
        Token.objects.create(user=user)
        
        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for user authentication (login)
    """
    username = serializers.CharField(
        required=True,
        help_text='Username for authentication'
    )
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        help_text='Password for authentication'
    )
    
    def validate(self, data):
        """
        Validate and authenticate the user
        """
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # Authenticate the user
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError(
                    'Invalid username or password.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )
            
            data['user'] = user
        else:
            raise serializers.ValidationError(
                'Both username and password are required.'
            )
        
        return data