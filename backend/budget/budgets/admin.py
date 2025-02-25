from django.contrib import admin
from .models import BudgetPlan, Category, Subcategory

@admin.register(BudgetPlan)
class BudgetPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_predefined', 'created_at')
    list_filter = ('is_predefined', 'created_at')
    search_fields = ('name', 'user_username')


@admin.register(Category)
class CategoryAdmiin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'budget_plan')
    list_filter = ('budget_plan',)
    search_fields = ('name',)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
