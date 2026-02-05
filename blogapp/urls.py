
from django.urls import path # type: ignore
from blogapp import views
from blogapp.views import *

print("Loading blogapp.urls...")

urlpatterns = [
    path('', IndexView.as_view()),
    path('login', LoginView.as_view(), name='login'),
    path("signup/", views.UserRegisterView.as_view(), name="signup"),

    path('logout', LogoutView.as_view(), name='logout'),

    ################################################### ADMIN VIEWS #####################################################

    path('adminhome', AdminHomeView.as_view(), name='adminhome'),
    path('users', ViewUserView.as_view(), name='users'),
    path('complaints', ComplaintView.as_view(), name='complaints'),
    path('feedback', ViewFeedback.as_view(), name='feedback'),
    path('verifyblog', VerifyBlog.as_view(), name='verifyblog'),
    path('ban/<int:id>', BanUser.as_view()),
    path('unban/<int:id>', UnBanUser.as_view()),
    path('acceptblog/<int:id>', AcceptBlog.as_view()),
    path('rejectblog/<int:id>', RejectBlog.as_view()),
    path("api/scan-blog-ai/", views.scan_blog_ai, name="scan_blog_ai"),


    #################################################  USER VIEWS  ###################################

    path('register', UserRegisterView.as_view(), name='register'),
    path('userhome', UserHome.as_view(), name='userhome'),
    path('otp', OTPVerification.as_view(), name='otp'),
    path('addblog', AddBlogView.as_view(), name='addblog'),
    
    # API Endpoints
    path("api/openrouter-blog-ai/", OpenRouterBlogAI.as_view(), name="openrouter_blog_ai"),

    path('api/load-more-blogs/', LoadMoreBlogs.as_view(), name='load_more_blogs'),
    path('api/toggle-like/', ToggleLikeAPI.as_view(), name='toggle_like'),
    path('api/add-comment/', AddCommentAPI.as_view(), name='add_comment'),
    path('api/add-complaint/', AddComplaintAPI.as_view(), name='add_complaint'),
    path('api/payment/', PaymentView.as_view(), name='payment'),
    
    path('blog/<int:id>/', BlogDetailView.as_view(), name='blog_detail'),
    path('plans', PlansView.as_view(), name='plans'),
    path('payment-gateway/', PaymentGatewayView.as_view(), name='payment_gateway'),
    path('support', UserSupportView.as_view(), name='user_support'),
    path('my-blogs', MyBlogView.as_view(), name='my_blogs'),
    path('edit-blog/<int:id>/', EditBlogView.as_view(), name='edit_blog'),
    path('delete-blog/<int:id>/', DeleteBlogView.as_view(), name='delete_blog'),
    path('blog-tts/<int:blog_id>/', views.blog_tts, name='blog_tts'),
    path('blog-full-tts/<int:blog_id>/', views.blog_full_tts, name='blog_full_tts'),
    path('edit-profile/', EditProfile.as_view(), name='edit_profile'),
    path('redeem-points/', RedeemPoint.as_view(), name='redeem_points'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('notifications/read/<int:id>/', MarkAsRead.as_view(), name='mark_notification_read'),
]
