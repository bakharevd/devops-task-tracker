from django.contrib import admin

from .models import Status, Priority, Task, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


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
        'id', 'title', 'project', 'creator', 'assignee', 'status', 'priority', 'created_at', 'due_date'
    )
    list_filter = ('project', 'status', 'priority', 'creator', 'assignee')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

    raw_id_fields = ('creator', 'assignee', 'project')
    autocomplete_fields = ('status', 'priority')
