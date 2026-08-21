from django.contrib import admin
from .models import Category, Challenge, Submission

class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'points', 'is_visible')
    list_filter = ('category', 'is_visible')
    search_fields = ('title', 'description')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'is_correct', 'timestamp')
    list_filter = ('is_correct', 'challenge', 'user')
    readonly_fields = ('timestamp',)

admin.site.register(Category)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Submission, SubmissionAdmin)
