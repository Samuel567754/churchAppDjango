from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from contact.models import SocialMediaMixin, ImageMixin


# DONATION MODEL
class Donation(models.Model):
    PAYMENT_METHODS = [
        ('paystack', 'Paystack'),  # Specifically for Paystack
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    PURPOSES = [
        ('offering', 'Offering'),
        ('building_fund', 'Building Fund'),
        ('wedding', 'Wedding'),
        ('benevolence', 'Benevolence'),
        ('visitation', 'Visitation'),
        ('edification', 'Edification'),
        ('worship', 'Worship'),
        ('funeral', 'Funeral'),
        ('other', 'Other'),
    ]

    donor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=50, choices=PURPOSES)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='paystack')
    is_recurring = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, blank=True, unique=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Donations"

    def __str__(self):
        return f"${self.amount} for {self.purpose} by {self.donor.username if self.donor else 'Anonymous'}"


# ASSET MODEL
class Asset(models.Model):
    ASSET_CONDITIONS = [
        ('Good', 'Good'),
        ('Needs Repair', 'Needs Repair'),
        ('Damaged', 'Damaged'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    purchase_date = models.DateField()
    value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=255, choices=ASSET_CONDITIONS, default='Good')

    class Meta:
        ordering = ['-purchase_date']
        verbose_name_plural = "Assets"

    def __str__(self):
        return f"{self.name} ({self.condition})"
