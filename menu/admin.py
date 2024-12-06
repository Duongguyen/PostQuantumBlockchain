from django.contrib.auth.admin import UserAdmin

from .models import *
from django.contrib import admin
from django.contrib.auth.models import User


class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'

class CustomizeUserAdmin (UserAdmin):
    inlines = (AccountInline, )


# Register your models here.
admin.site.register(Transaction)
admin.site.register(BlockchainUser)
admin.site.register(Blockchains)
admin.site.register(TitlePage)
admin.site.register(New)
admin.site.unregister(User)
admin.site.register(User, CustomizeUserAdmin)
