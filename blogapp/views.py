import random
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from blogapp.forms import *
from blogapp.models import *
from django.core.mail import send_mail
from django.core.paginator import Paginator


# Create your views here.
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')
    
class LogoutView(View):
    def get(self, request):
        return HttpResponse('''<script>alert('logged out successfully');window.location='/'</script>''')

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        try:
            obj = LoginModel.objects.get(Username=username, Password=password)
            request.session['user_id'] = obj.id
            if obj.usertype == "admin":
                return HttpResponse('''<script>alert("Welcome Back");window.location='/adminhome'</script>''') 

            elif obj.usertype == "USER":
                otp = str(random.randint(100000, 999999))   
                obj.otp = otp
                obj.otp_verified = False

                obj.save()

                send_mail(
                    subject= f"OTP for Login",
                    message= f"Your OTP For Logging to the Awaaz is {otp}",
                    from_email= None,
                    recipient_list= [obj.Username],
                    fail_silently= False,
                )

                return HttpResponse('''<script>alert("OTP sent to your email");window.location='/otp'</script>''')
            else:
                return HttpResponse('''<script>alert("Invalid User");window.location='/'</script>''')            
        except LoginModel.DoesNotExist:
            return HttpResponse('''<script>alert("Invalid Credentials");window.location='/'</script>''')
        
################################################### ADMIN VIEWS #####################################################

from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

class AdminHomeView(View):
    def get(self, request):
        total_users = UserModel.objects.count()
        total_blogs = BlogModel.objects.count()
        pending_blogs = BlogModel.objects.filter(status__iexact="pending").count() 
        complaints_count = ComplaintModel.objects.filter(Q(Reply__isnull=True) | Q(Reply__exact='')).count()

        today = timezone.localdate()
        dates = [today - timedelta(days=i) for i in range(29, -1, -1)]
        
        labels = [d.strftime('%b %d') for d in dates]
        new_users_data = []
        new_blogs_data = []

        for d in dates:
            new_users_data.append(UserModel.objects.filter(joined_at=d).count())
            new_blogs_data.append(BlogModel.objects.filter(created_at=d).count())

        context = {
            'total_users': total_users,
            'total_blogs': total_blogs,
            'pending_blogs': pending_blogs,
            'complaints_count': complaints_count,
            'chart_labels': json.dumps(labels),
            'user_data': json.dumps(new_users_data),
            'blog_data': json.dumps(new_blogs_data),
        }
        return render(request, 'administration/admin_home.html', context)
    

class ViewUserView(View):
    def get(self, request):
        users = UserModel.objects.all().order_by('-joined_at')

        paginator = Paginator(users, 4)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            'administration/viewUser.html',
            {
                'page_obj': page_obj,
            }
        )
    
class BanUser(View):
    def get(self, request, id):
        c = UserModel.objects.get(id=id)
        c.LOGINID.usertype = "Pending"
        c.LOGINID.save()
        return redirect('/users')
    
class UnBanUser(View):
    def get(self, request, id):
        c = UserModel.objects.get(id=id)
        c.LOGINID.usertype = "USER"
        c.LOGINID.save()
        return redirect('/users')

class ComplaintView(View):
    def get(self, request):
        c = ComplaintModel.objects.all().order_by('-id')
        return render(request, 'administration/viewcomplaint.html', {'complaint': c})

    def post(self, request):
        complaint_id = request.POST.get('complaint_id')
        reply = request.POST.get('reply')

        obj = ComplaintModel.objects.get(id=complaint_id)
        obj.Reply = reply
        obj.save()

        return redirect('/complaints')
    
class ViewFeedback(View):
    def get(self, request):
        f = FeedBackModel.objects.all().order_by('-created_at')
        return render(request, 'administration/viewfeedback.html', {'feedback': f})
    
class VerifyBlog(View):
    def get(self, request):
        c = BlogModel.objects.all().order_by('-created_at')
        return render(request, 'administration/verifyblog.html',{'c':c})
    
# from openai import OpenAI
# from django.http import JsonResponse
# from django.views import View
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# import json
# import re
# import traceback

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key="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"
# )

# @method_decorator(csrf_exempt, name="dispatch")
# class BlogModerationAI(View):

#     def post(self, request):
#         try:
#             data = json.loads(request.body)
#             content = data.get("content", "").strip()

#             if not content:
#                 return JsonResponse({"error": "Content required"}, status=400)

#             response = client.chat.completions.create(
#                 model="mistralai/mistral-7b-instruct:free",
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": (
#                             "You are a STRICT JSON API.\n"
#                             "Analyze text for abusive, hateful, vulgar, or personal attack content.\n"
#                             "You MUST return VALID JSON ONLY.\n"
#                             "No explanation. No extra text.\n\n"
#                             "JSON SCHEMA:\n"
#                             "{\n"
#                             '  "is_safe": boolean,\n'
#                             '  "issues": array of strings,\n'
#                             '  "severity": "low" | "medium" | "high"\n'
#                             "}"
#                         )
#                     },
#                     {
#                         "role": "user",
#                         "content": content
#                     }
#                 ],
#                 temperature=0.1
#             )

#             ai_text = response.choices[0].message.content.strip()

#             # ✅ HARD JSON EXTRACTION (most reliable)
#             json_match = re.findall(r"\{[\s\S]*?\}", ai_text)

#             if not json_match:
#                 print("RAW AI RESPONSE (SCAN):\n", ai_text)
#                 return JsonResponse({
#                     "is_safe": True,
#                     "issues": [],
#                     "severity": "low"
#                 })

#             json_str = json_match[-1]  # take last JSON block

#             try:
#                 result = json.loads(json_str)
#             except Exception:
#                 print("BROKEN JSON FROM AI:\n", json_str)
#                 return JsonResponse({
#                     "is_safe": True,
#                     "issues": [],
#                     "severity": "low"
#                 })

#             issues = result.get("issues", [])

#             return JsonResponse({
#                 "is_safe": result.get("is_safe", True),
#                 "issues": issues,
#                 "count": len(issues),
#                 "severity": result.get("severity", "low")
#             })

#         except Exception:
#             traceback.print_exc()
#             return JsonResponse({
#                 "is_safe": True,
#                 "issues": [],
#                 "severity": "low"
#             })

# from openai import OpenAI
# from django.http import JsonResponse
# from django.views import View
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# import json
# import re
# import traceback

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key="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"
# )

# @method_decorator(csrf_exempt, name="dispatch")
# class BlogModerationAI(View):

#     def post(self, request):
#         try:
#             data = json.loads(request.body)
#             content = data.get("content", "").strip()

#             if not content:
#                 return JsonResponse({"error": "Content required"}, status=400)

#             response = client.chat.completions.create(
#                 model="mistralai/mistral-7b-instruct:free",
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": (
#                             "You are a STRICT JSON content moderation API. Detect any negativity, insults, or disguised curse words.\n"
#                                 "Flag even mild abusive words (like 'stupid', 'dumb', 'idiot') and masked profanity (like 'a**hole', 'd*mn', 'b.s').\n"
#                                 "Detect personal attacks, toxic language, and rude comments.\n"
#                                 "Return ONLY valid JSON, no explanations or extra text.\n"
#                                 "JSON SCHEMA:\n"
#                                 "{\n"
#                                 '  "is_safe": boolean,\n'
#                                 '  "issues": array of strings (all negative words/phrases found),\n'
#                                 '  "severity": "low" | "medium" | "high"\n'
#                                 "}"
#                         )
#                     },
#                     {
#                         "role": "user",
#                         "content": content
#                     }
#                 ],
#                 temperature=0.1
#             )

#             ai_text = response.choices[0].message.content.strip()

#             # ✅ Extract JSON safely
#             json_match = re.findall(r"\{[\s\S]*?\}", ai_text)
#             if not json_match:
#                 print("RAW AI RESPONSE (SCAN):\n", ai_text)
#                 return JsonResponse({
#                     "is_safe": True,
#                     "issues": [],
#                     "severity": "low"
#                 })

#             json_str = json_match[-1]  # take last JSON block
#             try:
#                 result = json.loads(json_str)
#             except Exception:
#                 print("BROKEN JSON FROM AI:\n", json_str)
#                 return JsonResponse({
#                     "is_safe": True,
#                     "issues": [],
#                     "severity": "low"
#                 })

#             issues = result.get("issues", [])

#             return JsonResponse({
#                 "is_safe": result.get("is_safe", True),
#                 "issues": issues,
#                 "count": len(issues),
#                 "severity": result.get("severity", "low")
#             })

#         except Exception:
#             traceback.print_exc()
#             return JsonResponse({
#                 "is_safe": True,
#                 "issues": [],
#                 "severity": "low"
#             })

# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from transformers import pipeline

# # ---------------- LOAD MODELS (ONCE) ----------------
# toxicity_classifier = pipeline(
#     "text-classification",
#     model="unitary/toxic-bert",
#     return_all_scores=True
# )

# sentiment_analyzer = pipeline(
#     "sentiment-analysis",
#     model="distilbert-base-uncased-finetuned-sst-2-english"
# )

# # ---------------- THRESHOLDS (IMPORTANT) ----------------
# ISSUE_THRESHOLDS = {
#     "toxic": 0.35,
#     "severe_toxic": 0.50,
#     "insult": 0.30,
#     "obscene": 0.30,
#     "threat": 0.60,
#     "identity_hate": 0.50,
# }

# @csrf_exempt
# def scan_blog_ai(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=400)

#     try:
#         data = json.loads(request.body)
#         content = data.get("content", "").strip()

#         if not content:
#             return JsonResponse({
#                 "issues": [],
#                 "mood": "neutral",
#                 "risk": "LOW",
#                 "safe": True
#             })

#         # ---------------- TOXICITY ANALYSIS ----------------
#         toxicity_results = toxicity_classifier(content)[0]

#         issues = []
#         scores = {}

#         for item in toxicity_results:
#             label = item["label"]
#             score = item["score"]
#             scores[label] = round(score, 3)

#             threshold = ISSUE_THRESHOLDS.get(label, 0.5)
#             if score >= threshold:
#                 issues.append(label)

#         # ---------------- SENTIMENT (MOOD) ----------------
#         sentiment = sentiment_analyzer(content)[0]
#         mood = sentiment["label"].lower()  # positive / negative

#         # ---------------- RISK LOGIC ----------------
#         if scores.get("threat", 0) >= 0.6:
#             risk = "HIGH"
#             safe = False
#         elif scores.get("severe_toxic", 0) >= 0.5:
#             risk = "HIGH"
#             safe = False
#         elif any(label in issues for label in ["toxic", "insult", "obscene"]):
#             risk = "MODERATE"
#             safe = False
#         else:
#             risk = "LOW"
#             safe = True

#         return JsonResponse({
#             "issues": issues,        # toxic, insult, obscene, threat, etc.
#             "mood": mood,            # positive / negative
#             "risk": risk,            # LOW / MODERATE / HIGH
#             "safe": safe             # TRUE only if genuinely safe
#         })

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline
from langdetect import detect, LangDetectException

# ---------------- LOAD MODELS (ONCE) ----------------

# English toxicity model (English ONLY)
toxicity_classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    return_all_scores=True
)

# Multilingual sentiment model (supports Malayalam)
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-xlm-roberta-base-sentiment"
)

# ---------------- THRESHOLDS ----------------
ISSUE_THRESHOLDS = {
    "toxic": 0.35,
    "severe_toxic": 0.50,
    "insult": 0.30,
    "obscene": 0.30,
    "threat": 0.60,
    "identity_hate": 0.50,
}

@csrf_exempt
def scan_blog_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        content = data.get("content", "").strip()

        if not content:
            return JsonResponse({
                "issues": [],
                "mood": "neutral",
                "risk": "LOW",
                "safe": True,
                "language": "unknown"
            })

        # ---------------- LANGUAGE DETECTION ----------------
        try:
            language = detect(content)
        except LangDetectException:
            language = "unknown"

        issues = []
        scores = {}

        # ---------------- TOXICITY (ONLY FOR ENGLISH) ----------------
        if language == "en":
            toxicity_results = toxicity_classifier(content)[0]

            for item in toxicity_results:
                label = item["label"]
                score = item["score"]
                scores[label] = round(score, 3)

                threshold = ISSUE_THRESHOLDS.get(label, 0.5)
                if score >= threshold:
                    issues.append(label)
        else:
            # Honest handling for non-English
            scores = {}
            issues = []

        # ---------------- SENTIMENT (MULTILINGUAL) ----------------
        sentiment = sentiment_analyzer(content)[0]

        # Normalize sentiment labels
        sentiment_map = {
            "positive": "positive",
            "neutral": "neutral",
            "negative": "negative",
            "LABEL_0": "negative",
            "LABEL_1": "neutral",
            "LABEL_2": "positive"
        }

        mood = sentiment_map.get(sentiment["label"].lower(), "neutral")

        # ---------------- RISK LOGIC ----------------
        if language == "en":
            if scores.get("threat", 0) >= 0.6:
                risk = "HIGH"
                safe = False
            elif scores.get("severe_toxic", 0) >= 0.5:
                risk = "HIGH"
                safe = False
            elif any(label in issues for label in ["toxic", "insult", "obscene"]):
                risk = "MODERATE"
                safe = False
            else:
                risk = "LOW"
                safe = True
        else:
            # Non-English: no abuse detected, sentiment only
            risk = "LOW"
            safe = True

        return JsonResponse({
            "issues": issues,        # empty for Malayalam
            "mood": mood,            # correct for Malayalam
            "risk": risk,
            "safe": safe,
            "language": language     # en / ml / hi etc.
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class AcceptBlog(View):
    def get(self, request, id):
        blog = BlogModel.objects.get(id=id)
        blog.status = "Accepted"
        blog.save()

        # Create a notification for the user
        if blog.USERID:  # Ensure the blog has a user
            NotificationModel.objects.create(
                USERID=blog.USERID,
                message=f"Your blog '{blog.title}' has been accepted and published!"
            )

        return redirect('/verifyblog')


class RejectBlog(View):
    def get(self, request, id):
        blog = BlogModel.objects.get(id=id)
        blog.status = "Rejected"
        blog.save()

        # Create a notification for the user
        if blog.USERID:  # Ensure the blog has a user
            NotificationModel.objects.create(
                USERID=blog.USERID,
                message=f"Your blog '{blog.title}' has been rejected."
            )

        return redirect('/verifyblog')
    
#################################################  USER VIEWS  ###################################
from django.core.validators import validate_email


class UserRegisterView(View):
    def get(self, request):
        return render(request, 'user/register.html')
    def post(self, request):
        c = UserForm(request.POST, request.FILES)

        try:
            email = request.POST['email']
            validate_email(email)
        except:
            return HttpResponse('''<script>alert("Invalid Email Address");window.location="/signup/"</script>''')
        try:
            existing_user = LoginModel.objects.get(Username=request.POST['email'])
            if existing_user:
                return HttpResponse('''<script>alert("Email already registered");window.location="/signup/"</script>''')
        except LoginModel.DoesNotExist:
            pass

        if c.is_valid():
            reg = c.save(commit=False)
            user = LoginModel.objects.create(Username = reg.email, Password = request.POST['password'], usertype='USER')
            reg.LOGINID = user
            reg.save()
            return HttpResponse('''<script>alert("register successfully");window.location="/login"</script>''')
        
def annotate_blogs(blogs, user_id):
    for blog in blogs:
        blog.like_count = LikeModel.objects.filter(BLOGID=blog, like=True).count()
        blog.comment_count = LikeModel.objects.filter(BLOGID=blog, comment__isnull=False).exclude(comment='').count()
        blog.is_liked = LikeModel.objects.filter(BLOGID=blog, USERID__LOGINID__id=user_id, like=True).exists()
        # Fetch latest 2 comments for display
        blog.latest_comments = LikeModel.objects.filter(BLOGID=blog, comment__isnull=False).exclude(comment='').order_by('-id')[:2]
    return blogs

# class UserHome(View):
#     def get(self, request):
#         user_id = request.session.get('user_id')
#         c = UserModel.objects.filter(LOGINID__id=user_id).first()
        
#         # Filter Logic
#         category = request.GET.get('category')
#         blogs_qs = BlogModel.objects.filter(status='Accepted')
        
#         if category and category != 'All':
#             blogs_qs = blogs_qs.filter(category=category)
            
#         blogs = blogs_qs.order_by('-created_at')[:5]
#         blogs = annotate_blogs(blogs, user_id)
        
#         # Calculate Plan Validity
#         from django.utils import timezone
#         import datetime
        
#         remaining_days = 0
#         has_plan = False
#         payments = PaymentModel.objects.filter(USERID=c, payment_status='success')
        
#         for payment in payments:
#             expiry_date = payment.created_at + datetime.timedelta(days=payment.plan_duration_days)
#             if expiry_date > timezone.now():
#                 delta = expiry_date - timezone.now()
#                 remaining_days = delta.days
#                 has_plan = True
#                 break
        
#         # Fetch Reward Points
#         reward = RewardModel.objects.filter(USERID=c).first()
#         reward_points = reward.point if reward else 0

#         return render(request, 'user/userhome.html', {
#             'c': c, 
#             'blogs': blogs, 
#             'remaining_days': remaining_days, 
#             'has_plan': has_plan,
#             'reward_points': reward_points
#         })

from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

class UserHome(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        c = UserModel.objects.filter(LOGINID__id=user_id).first()

        # Filter Logic
        category = request.GET.get('category')
        language = request.GET.get('language', 'All')  # Get selected language, default All

        blogs_qs = BlogModel.objects.filter(status='Accepted')

        # Filter by category
        if category and category != 'All':
            blogs_qs = blogs_qs.filter(category=category)

        # Filter by language
        if language and language != 'All':
            filtered_blogs = []
            for blog in blogs_qs:
                try:
                    lang = detect(blog.blog)  # Detect language of blog text
                    if lang == language:
                        filtered_blogs.append(blog)
                except:
                    continue
            blogs_qs = filtered_blogs

        blogs = blogs_qs if isinstance(blogs_qs, list) else blogs_qs.order_by('-created_at')[:5]
        blogs = annotate_blogs(blogs, user_id)  # Assuming you have this function

        # Calculate Plan Validity
        from django.utils import timezone
        import datetime

        remaining_days = 0
        has_plan = False
        payments = PaymentModel.objects.filter(USERID=c, payment_status='success')

        for payment in payments:
            expiry_date = payment.created_at + datetime.timedelta(days=payment.plan_duration_days)
            if expiry_date > timezone.now():
                delta = expiry_date - timezone.now()
                remaining_days = delta.days
                has_plan = True
                break

        # Fetch Reward Points
        reward = RewardModel.objects.filter(USERID=c).first()
        reward_points = reward.point if reward else 0

        unread_count = NotificationModel.objects.filter(USERID=c, is_read=False).count()

        return render(request, 'user/userhome.html', {
            'c': c,
            'blogs': blogs,
            'remaining_days': remaining_days,
            'has_plan': has_plan,
            'reward_points': reward_points,
            'unread_count': unread_count,
            'language': language,  # Pass selected language to template
        })

from django.template.loader import render_to_string

class LoadMoreBlogs(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        # Fetch user object to pass for profile image in comments
        c = UserModel.objects.filter(LOGINID__id=user_id).first()
        
        offset = int(request.GET.get('offset', 5))
        category = request.GET.get('category')
        limit = 5
        
        blogs_qs = BlogModel.objects.filter(status='Accepted')
        if category and category != 'All':
            blogs_qs = blogs_qs.filter(category=category)
            
        blogs = blogs_qs.order_by('-created_at')[offset:offset + limit]
        
        if not blogs:
            return JsonResponse({'html': '', 'has_next': False})
        
        blogs = annotate_blogs(blogs, user_id)
        # Pass 'c' to context so partial can render user profile image
        html = render_to_string('user/blog_card_partial.html', {'blogs': blogs, 'c': c}, request=request)
        return JsonResponse({'html': html, 'has_next': True})
    
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name="dispatch")
class ToggleLikeAPI(View):
    def post(self, request):
        try:
            user_id = request.session.get('user_id')
            data = json.loads(request.body)
            blog_id = data.get('blog_id')
            
            user = UserModel.objects.get(LOGINID__id=user_id)
            blog = BlogModel.objects.get(id=blog_id)
            
            # Check for existing like interaction (where comment might be null or not)
            # We want to toggle the 'like' boolean specifically. 
            # Strategy: valid 'like' is a record where like=True.
            
            existing_like = LikeModel.objects.filter(USERID=user, BLOGID=blog, like=True).first()
            
            if existing_like:
                # Unlike
                existing_like.like = False
                existing_like.save()
                is_liked = False
            else:
                # Like - check if we can reuse a record (e.g. one that has a comment but like=False) 
                # or create new. For simplicity, let's create a new one if no pure like record exists, 
                # or update if we find one. 
                # ACTUALLY, LikeModel structure is a bit ambiguous (one row per like OR comment?).
                # Assuming one row can hold both, or separate rows. 
                # Use separate row for simple "Like" action if no record found.
                
                # Let's try to find ANY record for this user/blog to update, or create new.
                record = LikeModel.objects.filter(USERID=user, BLOGID=blog).first()
                if record:
                    record.like = True
                    record.save()
                else:
                    LikeModel.objects.create(USERID=user, BLOGID=blog, like=True)
                is_liked = True

            like_count = LikeModel.objects.filter(BLOGID=blog, like=True).count()
            
            # REWARD LOGIC: If likes > 100 and not rewarded, give reward
            if is_liked and like_count > 100 and not blog.is_rewarded:
                # Give Reward
                reward, created = RewardModel.objects.get_or_create(USERID=blog.USERID)
                if reward.point is None:
                    reward.point = 0
                reward.point += 50  # Award 50 points
                reward.save()
                
                # Mark blog as rewarded to prevent double counting
                blog.is_rewarded = True
                blog.save()

            return JsonResponse({'success': True, 'is_liked': is_liked, 'like_count': like_count})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name="dispatch")
class AddCommentAPI(View):
    def post(self, request):
        try:
            user_id = request.session.get('user_id')
            data = json.loads(request.body)
            blog_id = data.get('blog_id')
            comment_text = data.get('comment')
            
            if not comment_text:
                 return JsonResponse({'success': False, 'error': "Empty comment"})

            user = UserModel.objects.get(LOGINID__id=user_id)
            blog = BlogModel.objects.get(id=blog_id)
            
            # Create a new record for every comment
            new_comment = LikeModel.objects.create(USERID=user, BLOGID=blog, comment=comment_text, like=False)
            
            comment_count = LikeModel.objects.filter(BLOGID=blog, comment__isnull=False).exclude(comment='').count()

            # Return the HTML for the new comment to append
            html = f'''
            <div class="flex items-start space-x-3 fade-in">
                <img src="{user.profile.url if user.profile else 'https://via.placeholder.com/150'}" alt="User" class="w-10 h-10 rounded-full border-2 border-[#667eea]">
                <div class="flex-1 bg-gray-50 rounded-2xl px-4 py-3">
                    <p class="font-medium text-sm">{user.Name}</p>
                    <p class="text-gray-700 text-sm mt-1">{comment_text}</p>
                </div>
            </div>
            '''
            return JsonResponse({'success': True, 'html': html, 'comment_count': comment_count})
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name="dispatch")
class AddComplaintAPI(View):
    def post(self, request):
        try:
            user_id = request.session.get('user_id')
            data = json.loads(request.body)
            blog_id = data.get('blog_id')
            subject = data.get('subject')
            complaint_text = data.get('complaint')
            
            if not complaint_text or not subject:
                 return JsonResponse({'success': False, 'error': "Subject and Complaint are required"})

            user = UserModel.objects.filter(LOGINID__id=user_id).first()
            blog = BlogModel.objects.get(id=blog_id)
            
            ComplaintModel.objects.create(
                USERID=user, 
                BLOGID=blog, 
                Subject=subject, 
                Complaint=complaint_text
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})

class BlogDetailView(View):
    def get(self, request, id):
        user_id = request.session.get('user_id')
        c = UserModel.objects.filter(LOGINID__id=user_id).first()
        
        # Check for active subscription
        # Simplified: Check if any successful payment exists. 
        # Ideally, check expiry date (created_at + plan_duration_days > now)
        from django.utils import timezone
        import datetime
        
        has_active_plan = False
        payments = PaymentModel.objects.filter(USERID=c, payment_status='success')
        
        for payment in payments:
            expiry_date = payment.created_at + datetime.timedelta(days=payment.plan_duration_days)
            if expiry_date > timezone.now():
                has_active_plan = True
                break
        
        # If no active plan, redirect to plans page
        if not has_active_plan:
            return redirect('/plans')

        from django.shortcuts import get_object_or_404
        blog = get_object_or_404(BlogModel, id=id)
        return render(request, 'user/blog_detail.html', {'blog': blog, 'c': c})

class PlansView(View):
    def get(self, request):
        return render(request, 'user/plans.html')

class PaymentGatewayView(View):
    def get(self, request):
        plan = request.GET.get('plan', 'basic')
        amount = request.GET.get('amount', '0')
        days = request.GET.get('days', '0')
        
        # Mapping plan codes to nice names is optional but good
        plan_names = {
            'quarterly': 'Quarterly Plan',
            'half-yearly': 'Half-Yearly Plan',
            'annual': 'Annual Premium'
        }
        
        context = {
            'plan': plan,
            'plan_name': plan_names.get(plan, plan.title()),
            'amount': amount,
            'days': days
        }
        return render(request, 'user/payment_gateway.html', context)

@method_decorator(csrf_exempt, name="dispatch")
class PaymentView(View):
    def post(self, request):
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()
        
        plan = request.POST.get('plan')
        amount = request.POST.get('amount')
        days = int(request.POST.get('days', 30))
        method = request.POST.get('payment_method', 'card')
        upi_id = request.POST.get('upi_id', '')
        
        # Create dummy successful payment
        PaymentModel.objects.create(
            USERID=user,
            plan=plan,
            plan_amount=amount,
            plan_duration_days=days,
            payment_method=method,
            upi_id=upi_id if method == 'upi' else None,
            payment_status='success',
            transaction_id=f"TXN_{random.randint(100000,999999)}"
        )
        
        return HttpResponse('''<script>alert("Payment Successful! Plan Activated.");window.location='/userhome'</script>''')
    

class OTPVerification(View):
    def get(self, request):
        c = LoginModel.objects.get(id = request.session['user_id'])
        return render(request, 'user/otp.html', {'c':c})
    def post(self, request):
        entered_otp = request.POST.get('otp')

        print("ENTERED OTP:", entered_otp)

        

        try:
            user = LoginModel.objects.get(id = request.session['user_id'])


            if str(user.otp).strip() == str(entered_otp):
                user.otp_verified = True
                user.otp = None
                user.save()

                return HttpResponse(
                    '''<script>alert("OTP Verified Successfully");window.location='/userhome'</script>'''
                )
            else:
                return HttpResponse(
                    '''<script>alert("Invalid OTP");window.location='/otp'</script>'''
                )

        except LoginModel.DoesNotExist:
            return HttpResponse(
                '''<script>alert("Invalid User");window.location='/'</script>'''
            )
        

class UserSupportView(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()
        complaints = ComplaintModel.objects.filter(USERID=user).order_by('-created_at')
        return render(request, 'user/support.html', {'c': user, 'complaints': complaints})

    def post(self, request):
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()
        
        feedback_text = request.POST.get('feedback')
        rating = request.POST.get('rating', '5')
        
        FeedBackModel.objects.create(
            USERID=user,
            Feedback=feedback_text,
            rating=rating
        )
        
        return HttpResponse('<script>alert("Feedback Submitted Successfully!");window.location="/support"</script>')

class MyBlogView(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()
        blogs = BlogModel.objects.filter(USERID=user).order_by('-created_at')
        return render(request, 'user/myblog.html', {'blogs': blogs, 'c': user})

class EditBlogView(View):
    def get(self, request, id):
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()
        blog = BlogModel.objects.get(id=id)
        # Ensure user owns the blog
        if blog.USERID != user:
            return HttpResponse("Unauthorized", status=403)
            
        return render(request, 'user/EditBlog.html', {'blog': blog, 'c': user})

    def post(self, request, id):
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()
        blog = BlogModel.objects.get(id=id)
        
        if blog.USERID != user:
             return HttpResponse("Unauthorized", status=403)
             
        # Update fields
        title = request.POST.get('title')
        category = request.POST.get('category')
        content = request.POST.get('blog')
        
        if title: blog.title = title
        if category: blog.category = category
        if content: blog.content = content
        
        # Update Image if provided
        if 'Image' in request.FILES:
            blog.Image = request.FILES['Image']
            
        # Optional: Reset verification status on edit? 
        # For now, let's keep it simple or reset to pending
        # blog.is_verified = 'pending' 
        
        blog.save()
        return HttpResponse('''<script>alert("Blog Updated Successfully!");window.location="/my-blogs"</script>''')

class DeleteBlogView(View):
    def get(self, request, id):
        # Using GET for simplicity in a simple app, ideally DELETE or POST
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()
        try:
            blog = BlogModel.objects.get(id=id)
            if blog.USERID == user:
                blog.delete()
                return HttpResponse('''<script>alert("Blog Deleted Successfully!");window.location="/my-blogs"</script>''')
            else:
                return HttpResponse("Unauthorized", status=403)
        except BlogModel.DoesNotExist: 
             return HttpResponse("Blog not found", status=404)

class AddBlogView(View):
    def get(self, request):
        c = UserModel.objects.get(LOGINID__id=request.session['user_id'])
        blogs = BlogModel.objects.filter(USERID=c, parent__isnull=True)  # For parent dropdown
        return render(request, 'user/addblog.html', {'c': c, 'blogs': blogs})

    def post(self, request):
        c = UserModel.objects.get(LOGINID__id=request.session['user_id'])
        blog = BlogForm(request.POST, request.FILES)

        if blog.is_valid():
            reg = blog.save(commit=False)  # Don't save yet
            reg.USERID = c
            reg.status = "Pending"

            # Handle optional parent
            parent_id = request.POST.get('parent')
            if parent_id:  # Only assign if a parent is selected
                try:
                    parent_blog = BlogModel.objects.get(id=parent_id)
                    reg.parent = parent_blog
                except BlogModel.DoesNotExist:
                    reg.parent = None  # Safety fallback
            else:
                reg.parent = None  # No parent selected

            reg.save()
            return redirect('/userhome')

    


# from openai import OpenAI
# from django.http import JsonResponse
# from django.views import View
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# import json
# import traceback
# import re


# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key="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"
# )


# @method_decorator(csrf_exempt, name="dispatch")
# class OpenRouterBlogAI(View):

#     def post(self, request):
#         try:
#             data = json.loads(request.body)
#             blog_content = data.get("content", "").strip()

#             if not blog_content:
#                 return JsonResponse(
#                     {"error": "Blog content is required"},
#                     status=400
#                 )

#             response = client.chat.completions.create(
#                 model="mistralai/mistral-7b-instruct",
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": (
#                             "You are a helpful assistant. Generate a short, catchy blog title for the provided content.\n"
#                             "Reply PURELY with the title text. Do not use JSON. Do not add quotes or prefixes like 'Title:'."
#                         )
#                     },
#                     {
#                         "role": "user",
#                         "content": blog_content
#                     }
#                 ],
#                 temperature=0.7
#             )

#             ai_text = response.choices[0].message.content.strip()
            
#             # Cleanup text (remove quotes, prefixes)
#             title = ai_text.replace('Title:', '').replace('title:', '').strip().strip('"').strip("'")

#             return JsonResponse({"title": title, "corrected_text": ""})

#         except Exception as e:
#             error_msg = str(e)
#             if "401" in error_msg:
#                 error_msg = "Invalid API Key. Please check your OpenRouter key."
            
#             print(f"AI Error: {error_msg}")
#             return JsonResponse(
#                 {"error": f"Internal server error: {str(e)}"},
#                 status=500
#             )
from openai import OpenAI
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from langdetect import detect
import json

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

@method_decorator(csrf_exempt, name="dispatch")
class OpenRouterBlogAI(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            blog_content = data.get("content", "").strip()

            if not blog_content:
                return JsonResponse(
                    {"error": "Blog content is required"},
                    status=400
                )

            # -------- LANGUAGE DETECTION --------
            try:
                language = detect(blog_content)
            except:
                language = "unknown"

            # -------- UNIVERSAL SYSTEM PROMPT --------
            system_prompt = f"""
You are a helpful assistant.

The blog content is written in the language: {language}.
Generate a SHORT, SIMPLE, MEANINGFUL BLOG TITLE (1–5 words only).

CRITICAL RULES:
- The title MUST be written STRICTLY in the SAME language as the blog content ({language}).
- DO NOT translate to any other language.
- DO NOT switch to English unless the blog itself is English.
- DO NOT reuse, copy, or paraphrase the first line.
- The title must be an abstract heading, NOT a sentence.
- DO NOT include quotes, punctuation, emojis, or explanations.

Reply ONLY with the title text.
"""

            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": blog_content}
                ],
                temperature=0.5
            )

            ai_text = response.choices[0].message.content.strip()

            # Final cleanup safeguard
            title = (
                ai_text
                .replace("Title:", "")
                .replace("title:", "")
                .strip()
                .strip('"')
                .strip("'")
            )

            return JsonResponse({
                "title": title,
                "language": language
            })

        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=500
            )



from django.http import HttpResponse
from gtts import gTTS
from io import BytesIO
from django.utils.text import Truncator
from langdetect import detect, LangDetectException


# def blog_tts(request, blog_id):
#     blog = BlogModel.objects.get(id=blog_id)

#     # 🔥 Truncate to SAME 30 words
#     text = Truncator(blog.blog).words(30, truncate='')

#     tts = gTTS(text=text, lang='en')
#     fp = BytesIO()
#     tts.write_to_fp(fp)
#     fp.seek(0)

#     return HttpResponse(fp.read(), content_type='audio/mpeg')


def blog_tts(request, blog_id):
    blog = BlogModel.objects.get(id=blog_id)

    # Truncate same as frontend
    text = Truncator(blog.blog).words(30, truncate='')

    # 🌍 Detect language
    try:
        lang = detect(text)
    except LangDetectException:
        lang = 'en'   # fallback

    # Convert text to speech
    tts = gTTS(text=text, lang=lang)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    return HttpResponse(fp.read(), content_type='audio/mpeg')



def blog_full_tts(request, blog_id):
    blog = BlogModel.objects.get(id=blog_id)

    text = blog.blog.strip()

    # 🌍 Detect language (Malayalam works here)
    try:
        lang = detect(text)
    except LangDetectException:
        lang = 'en'

    tts = gTTS(text=text, lang=lang, slow=False)

    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    return HttpResponse(fp.read(), content_type='audio/mpeg')


class EditProfile(View):
    def get(self, request):
        c = UserModel.objects.get(LOGINID__id = request.session['user_id'])
        return render(request, 'user/edit_profile.html', {'c': c})
    def post(self, request):
        c = UserModel.objects.get(LOGINID__id = request.session['user_id'])
        c.Name = request.POST.get('Name')
        c.Phone = request.POST.get('Phone')
        c.Address = request.POST.get('Address')
        if 'profile' in request.FILES:
            c.profile = request.FILES['profile']
        c.save()
        return HttpResponse('''<script>alert("Profile Updated Successfully");window.location="/userhome"</script>''')
    
from decimal import Decimal


class RedeemPoint(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()

        # Fetch account if exists
        account = AccountModel.objects.filter(USERID=user).first()

        # Fetch reward points
        reward = RewardModel.objects.filter(USERID=user).first()
        reward_points = reward.point if reward else 0
        redeemable_amount = Decimal(reward_points) / Decimal(10)  # 10 points = ₹1

        # Eligibility
        eligible = redeemable_amount >= 1

        return render(request, 'user/Redeem_points.html', {
            'user': user,
            'account': account,
            'reward_points': reward_points,
            'redeemable_amount': redeemable_amount,
            'eligible': eligible
        })

    def post(self, request):
        user_id = request.session.get('user_id')
        user = UserModel.objects.filter(LOGINID__id=user_id).first()

        # Fetch reward points
        reward = RewardModel.objects.filter(USERID=user).first()
        reward_points = reward.point if reward else 0
        redeemable_amount = Decimal(reward_points) / Decimal(10)  # 10 points = ₹1

        if redeemable_amount < 1:
            return HttpResponse('''
                <script>
                    alert("You are not eligible to redeem. Minimum 10 points required (₹1).");
                    window.location="/redeem-points"
                </script>
            ''')

        # Update or create account details
        account, created = AccountModel.objects.get_or_create(USERID=user)
        account.account_holder_name = request.POST.get('account_holder_name')
        account.bank_name = request.POST.get('bank_name')
        account.branch_name = request.POST.get('branch_name')
        account.account_number = request.POST.get('account_number')
        account.ifsc_code = request.POST.get('ifsc_code')
        account.upi_id = request.POST.get('upi_id')

        # Add redeemed amount to balance
        account.balance += redeemable_amount
        account.save()

        # Deduct points after redemption
        if reward:
            reward.point = 0
            reward.save()

        return HttpResponse(f'''
            <script>
                alert("Redemption Request Submitted Successfully. ₹{redeemable_amount} credited to your account.");
                window.location="/redeem-points"
            </script>
        ''')
    

class NotificationsView(View):
    def get(self, request):
        user_id = request.session.get('user_id')
        user = UserModel.objects.get(LOGINID__id=user_id)
        
        # Fetch all notifications for this user
        notifications = NotificationModel.objects.filter(USERID=user).order_by('-created_at')

        # Count unread
        unread_count = notifications.filter(is_read=False).count()

        return render(request, 'user/notifications.html', {
            'notifications': notifications,
            'unread_count': unread_count
        })


class MarkAsRead(View):
    def get(self, request, id):
        notif = NotificationModel.objects.get(id=id)
        notif.is_read = True
        notif.save()
        return redirect('/notifications')  # Go back to notifications page