from django.contrib import admin

from blogapp.models import *

# Register your models here.
admin.site.register(LoginModel)
admin.site.register(UserModel)
admin.site.register(RewardModel)
admin.site.register(BlogModel)
admin.site.register(LikeModel)
admin.site.register(ComplaintModel)
admin.site.register(PaymentModel)
admin.site.register(AccountModel)
admin.site.register(FeedBackModel)
admin.site.register(NotificationModel)