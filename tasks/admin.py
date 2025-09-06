from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Task model
    """
    # Fields to display in the list view
    list_display = [
        'id', 'user', 'title', 'status', 
        'due_date', 'created_at', 'updated_at'
    ]
    
    # Fields that can be used to filter the list
    list_filter = ['status', 'created_at', 'due_date', 'user']
    
    # Fields that can be searched
    search_fields = ['title', 'description', 'user__username', 'user__email']
    
    # Fields that can be edited directly in the list view
    list_editable = ['status']
    
    # Default ordering in the admin panel
    ordering = ['-created_at']
    
    # Date hierarchy navigation
    date_hierarchy = 'created_at'
    
    # Fields to display when viewing/editing a single task
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'title', 'description', 'status', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Make this section collapsible
        }),
    )
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at']
    
    # Number of items to show per page
    list_per_page = 25
    
    # Enable actions
    actions = ['mark_as_completed', 'mark_as_pending']
    
    def mark_as_completed(self, request, queryset):
        """
        Custom admin action to mark selected tasks as completed
        """
        updated = queryset.update(status='completed')
        self.message_user(
            request,
            f'{updated} task(s) marked as completed.'
        )
    mark_as_completed.short_description = 'Mark selected tasks as completed'
    
    def mark_as_pending(self, request, queryset):
        """
        Custom admin action to mark selected tasks as pending
        """
        updated = queryset.update(status='pending')
        self.message_user(
            request,
            f'{updated} task(s) marked as pending.'
        )
    mark_as_pending.short_description = 'Mark selected tasks as pending'
    
    def get_queryset(self, request):
        """
        Override to optimize database queries
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')