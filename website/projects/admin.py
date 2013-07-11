from django.contrib import admin

from .models import Country, Project


class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'updated', 'is_active')
    list_filter = ('is_active',)
    readonly_fields = ('created', 'updated')
    filter_horizontal = ('countries',)
    fieldsets = (
        (None,
            {'fields': ('created', 'updated', 'creator', 'name', 'slug',
                    'status', 'is_active')},
        ),
        ('Project Information',
            {'fields': ('started', 'countries', 'description', 'challenges',
                    'audience', 'technologies', 'metrics', 'num_users',
                    'repository_url', 'packages', 'tags')},
        ),
    )


admin.site.register(Project, ProjectAdmin)
admin.site.register(Country)
