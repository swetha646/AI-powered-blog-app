# AI Coding Instructions for SmartBlog

## Architecture Overview
SmartBlog is a Django-based blogging platform with user authentication, content creation, and AI-powered features. Key components:
- **blogapp**: Main app with models (UserModel, BlogModel, etc.), views, and templates
- **Authentication**: Custom LoginModel with OTP verification via email
- **Content**: Blogs with categories, images, likes, comments, and moderation
- **Admin Panel**: Dashboard for user management, blog approval, complaints, and feedback
- **AI Integration**: OpenRouter API for generating blog titles from content
- **Payments**: Subscription plans with dummy payment gateway

## Key Workflows
- **Development Server**: `python manage.py runserver`
- **Database**: `python manage.py makemigrations && python manage.py migrate`
- **Superuser**: `python manage.py createsuperuser`
- **Static Files**: Served via `STATIC_URL = 'static/'` and `STATICFILES_DIRS`
- **Media Files**: Uploaded to `media/` directory, served via `MEDIA_URL = '/media/'`

## Project Conventions
- **Models**: Use `Model` suffix (e.g., `UserModel`), foreign keys reference IDs (e.g., `USERID = models.ForeignKey(UserModel)`)
- **Views**: Class-based views extending `View`, handle GET/POST
- **Templates**: Located in `templates/`, use Tailwind CSS for styling
- **URLs**: Defined in `blogapp/urls.py`, include API endpoints for AJAX interactions
- **Forms**: ModelForm subclasses for CRUD operations
- **AJAX**: Used for likes, comments, complaints via `/api/` endpoints
- **Email**: SMTP via Gmail for OTP and notifications
- **File Uploads**: Images stored in `media/blogimage/` and `media/profileimage/`

## Integration Points
- **OpenRouter AI**: Client initialized with `base_url="https://openrouter.ai/api/v1"`, used in `OpenRouterBlogAI` view for title generation
- **Email Backend**: Configured in `settings.py` with Gmail credentials
- **Payment Gateway**: Dummy implementation with UPI/Card/Net Banking options
- **Web Speech API**: Used in `addblog.html` for voice-to-text blog content input

## Common Patterns
- **Session Management**: User ID stored in `request.session['user_id']`
- **Status Fields**: Blogs have `status` ('pending', 'approved', 'rejected'), users have `usertype` ('USER', 'admin')
- **Pagination**: Used in blog listings with `Paginator`
- **CSRF Exemption**: Applied to API views like `OpenRouterBlogAI` for AJAX requests
- **Error Handling**: Basic try/except in views, redirect with JavaScript alerts
- **Responsive Design**: Templates use Tailwind classes for mobile-first design

## Debugging Tips
- Check browser console for AJAX errors
- Verify OpenRouter API key for AI features
- Ensure email credentials are correct for OTP
- Use Django admin at `/admin/` for data inspection
- Check `db.sqlite3` for database state

Reference files: `models.py`, `views.py`, `urls.py`, `settings.py`, `addblog.html` for voice recording.