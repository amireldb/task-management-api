from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer, UserSerializer, AuthTokenSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations.
    Users can only access their own tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Fields that can be used for filtering
    filterset_fields = ['status', 'due_date']
    
    # Fields that can be searched
    search_fields = ['title', 'description']
    
    # Fields that can be used for ordering
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'status']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """
        Filter tasks to only show tasks belonging to the authenticated user
        """
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        return Task.objects.none()
    
    def perform_create(self, serializer):
        """
        Automatically set the user field to the current authenticated user
        when creating a new task
        """
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """
        Ensure the user field cannot be changed during update
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Custom action to get only pending tasks for the current user
        """
        pending_tasks = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """
        Custom action to get only completed tasks for the current user
        """
        completed_tasks = self.get_queryset().filter(status='completed')
        serializer = self.get_serializer(completed_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Custom action to get overdue tasks for the current user
        """
        from django.utils import timezone
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status='pending'
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Custom action to mark a task as completed
        """
        task = self.get_object()
        task.status = 'completed'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to add custom message on successful deletion
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Task deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class UserRegistrationView(APIView):
    """
    API view for user registration.
    Creates a new user and returns authentication token.
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        """
        Handle POST request for user registration
        """
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create the user
            user = serializer.save()
            
            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # Return user data with token
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'token': token.key,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLoginView(APIView):
    """
    API view for user login.
    Authenticates user and returns authentication token.
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        """
        Handle POST request for user login
        """
        serializer = AuthTokenSerializer(data=request.data)
        
        if serializer.is_valid():
            # Get the authenticated user from serializer
            user = serializer.validated_data['user']
            
            # Get or create token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # Return user data with token
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLogoutView(APIView):
    """
    API view for user logout.
    Deletes the authentication token.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Handle POST request for user logout
        """
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Error during logout'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    """
    API view to get the current user's profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get current user's profile information
        """
        user = request.user
        task_count = user.tasks.count()
        pending_tasks = user.tasks.filter(status='pending').count()
        completed_tasks = user.tasks.filter(status='completed').count()
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined
            },
            'statistics': {
                'total_tasks': task_count,
                'pending_tasks': pending_tasks,
                'completed_tasks': completed_tasks
            }
        })

