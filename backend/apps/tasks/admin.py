from django.contrib import admin

from .models import Status, Priority, Task


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('id', 'level')
    search_fields = ('level',)
    ordering = ('id',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'creator', 'assignee', 'status', 'priority', 'created_at', 'due_date'
    )
    list_filter = ('status', 'priority', 'creator', 'assignee')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

    raw_id_fields = ('creator', 'assignee')
    autocomplete_fields = ('status', 'priority')
