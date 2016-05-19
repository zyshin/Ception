from django.contrib import admin
from .models import Activity, Notification, Log, ApplyLog


admin.site.register(Activity)
admin.site.register(Notification)
admin.site.register(Log)
admin.site.register(ApplyLog)
