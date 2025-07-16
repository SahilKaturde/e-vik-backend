from django.contrib import admin
from .models import Ewaste, DropCenter, EcoPoint,Reward


@admin.action(description='✅ Approve and assign drop location (Sadashiv Peth)')
def approve_ewaste(modeladmin, request, queryset):
    drop_center = DropCenter.objects.first()
    for ewaste in queryset:
        ewaste.status = 'approved'
        ewaste.drop_location = drop_center
        ewaste.save()


class EwasteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'drop_location', 'created_at')
    list_filter = ('status',)
    actions = [approve_ewaste]


admin.site.register(Ewaste, EwasteAdmin)
admin.site.register(DropCenter)
admin.site.register(EcoPoint)
admin.site.register(Reward)
