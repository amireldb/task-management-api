from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Task(models.Model):
    """
    Task model representing a task in the task management system.
    Each task belongs to a specific user and has status tracking.
    """
    
    # Status choices for the task
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    
    # User who owns this task (CASCADE: delete tasks when user is deleted)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        help_text='User who owns this task'
    )
    
    # Task details
    title = models.CharField(
        max_length=255,
        help_text='Title of the task'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed description of the task'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the task'
    )
    
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Due date and time for the task'
    )
    
    # Timestamps for tracking creation and updates
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the task was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the task was last updated'
    )
    
    class Meta:
        # Order tasks by creation date (newest first) by default
        ordering = ['-created_at']
        # Add database indexes for better query performance
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['due_date']),
        ]
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        """String representation of the task"""
        return f"{self.title} - {self.user.username}"
    
    def clean(self):
        """Validate the task data before saving"""
        super().clean()
        # Ensure due_date is not in the past when creating a new task
        if self.due_date and not self.pk:  # Only check for new tasks
            if self.due_date < timezone.now():
                raise ValidationError({'due_date': 'Due date cannot be in the past.'})
    
    def save(self, *args, **kwargs):
        """Override save to perform full validation"""
        self.full_clean()
        super().save(*args, **kwargs)