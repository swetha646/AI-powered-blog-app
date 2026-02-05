from django.db import models

# Create your models here.

class LoginModel(models.Model):
    Username = models.CharField(max_length=100, null=True, blank=True)
    Password = models.CharField(max_length=100, null=True, blank=True)
    usertype = models.CharField(max_length=100, null=True, blank=True)

    otp = models.IntegerField(null=True, blank=True)
    otp_verified = models.BooleanField(null=True, blank=True)


class UserModel(models.Model):
    LOGINID = models.ForeignKey(LoginModel, on_delete=models.CASCADE, null=True, blank=True)
    Name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    Phone = models.BigIntegerField(null=True, blank=True)
    Address = models.TextField(null=True, blank=True)
    profile = models.FileField(upload_to='profileimage/', null=True, blank=True)
    joined_at = models.DateField(auto_now_add=True, null=True, blank=True)


class RewardModel(models.Model):
    USERID = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    point = models.IntegerField(null=True, blank=True)

class BlogModel(models.Model):
    USERID = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='parts')
    category = models.CharField(max_length=100, null=True, blank=True)
    blog = models.TextField(null=True, blank=True)
    Image = models.FileField(upload_to='blogimage/', null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    is_rewarded = models.BooleanField(default=False)


class LikeModel(models.Model):
    USERID = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    BLOGID = models.ForeignKey(BlogModel, on_delete=models.CASCADE, null=True, blank=True)
    like = models.BooleanField(null=True, blank=True)
    comment = models.CharField(max_length=100, null=True, blank=True)

class ComplaintModel(models.Model):
    USERID = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    BLOGID = models.ForeignKey(BlogModel, on_delete=models.CASCADE, null=True, blank=True)
    Subject = models.CharField(max_length=100, null=True, blank=True)
    Complaint = models.TextField(null=True, blank=True)
    Reply = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)


class FeedBackModel(models.Model):
    USERID = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    Feedback = models.TextField(null=True, blank=True)
    rating = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)    

class PaymentModel(models.Model):

    PLAN_CHOICES = (
        ("basic", "Basic Plan"),
        ("standard", "Standard Plan"),
        ("premium", "Premium Plan"),
    )

    PAYMENT_METHOD = (
        ("upi", "UPI"),
        ("card", "Card"),
        ("netbanking", "Net Banking"),
        ("cash", "Cash"),
    )

    PAYMENT_STATUS = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    USERID = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="basic"
    )

    plan_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    plan_duration_days = models.PositiveIntegerField(
        help_text="Plan validity in days"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD
    )

    upi_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.USERID} - {self.plan} - ₹{self.plan_amount}"

class AccountModel(models.Model):
    USERID = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="account"
    )
    bank_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    branch_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    account_number = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Dummy account number"
    )

    ifsc_code = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.USERID} - Balance ₹{self.balance}"


class NotificationModel(models.Model):
    USERID = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)