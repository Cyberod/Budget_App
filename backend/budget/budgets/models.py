from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid
from django.core.exceptions import ValidationError
from django.db.models import Sum

class BudgetPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_predefined = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    budget_plan = models.ForeignKey(BudgetPlan, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.name} - {self.percentage}%"
    
    def clean(self):
        # skip if validation for new objects dont have an ID
        if not self.budget_plan_id:
            return
        
        # Get total percentage excluding this category(if it exists)
        existing_total = Category.objects.filter(budget_plan=self.budget_plan)
        if self.pk:
            existing_total = existing_total.exclude(pk=self.pk)
        existing_total = existing_total.aggregate(total=Sum('percentage'))['total'] or 0

        # Check if total will exceed 100%
        if existing_total + self.percentage > 100:
            raise ValidationError(f"Total percentage cannot exceed 100. Current total: {existing_total}%")
        

        def save(self, *args, **kwargs):
            self.clean()
            super().save(*args, **kwargs)


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.percentage}%"


    def clean(self):
        # Skip validation for new objects that don't have a Category yet
        if not self.category_id:
            return
            
        # Get total percentage excluding this subcategory (if it exists)
        existing_total = Subcategory.objects.filter(category=self.category)
        if self.pk:
            existing_total = existing_total.exclude(pk=self.pk)
        existing_total = existing_total.aggregate(total=Sum('percentage'))['total'] or 0
        
        # Check if total would exceed 100%
        if existing_total + self.percentage > 100:
            raise ValidationError(f"Total percentage cannot exceed 100%. Current total: {existing_total}%")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True) # e.g., USD, EUR, GBP
    name = models.CharField(max_length=100) # e.g., US Dollar
    symbol = models.CharField(max_length=5) # e.g., $, €, £

    def __str__(self):
        return f"{self.code} - {self.name}"

