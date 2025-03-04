import graphene
from django.db import models
from .types import BudgetPlanType, CategoryType, SubcategoryType
from budgets.models import BudgetPlan, Category, Subcategory
import re


class CreateBudgetPlan(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        is_predefined = graphene.Boolean(default_value=False)

    budget_plan = graphene.Field(BudgetPlanType)

    @classmethod
    def mutate(cls, root, info, name, user, is_predefined=False):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to create a Budget plan")
        if is_predefined and not user.is_staff:
            raise Exception("Only admins can create predefined plans")
        
        budget_plan = BudgetPlan(
            name=name,
            is_predefined=is_predefined,
            user=user
        )
        budget_plan.save()
        return CreateBudgetPlan(budget_plan=budget_plan)
        
    

class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        percentage = graphene.Decimal(required=True)
        budget_plan_id = graphene.ID(required=True)

    Category = graphene.Field(CategoryType)

    def mutate(self, info, name, percentage, budget_plan_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to create a category")
        
        budget_plan = BudgetPlan.objects.get(pk=budget_plan_id)
        if budget_plan.user != user:
            raise Exception("You can only add categories to your own budget plans")

        existing_total = Category.objects.filter(budget_plan=budget_plan).aggregate(
            total=models.Sum('percentage'))['total'] or 0

        # Check if the total would exceed 100%
        new_total = existing_total + percentage
        if new_total > 100:
            raise Exception(f"Total Percentage cannot be more than 100%. Current total: {existing_total}%")
        
        category = Category(
            name=name,
            percentage=percentage,
            budget_plan=budget_plan
        )
        category.save()
        return CreateCategory(Category=category)
    

class CreateSubcategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        percentage = graphene.Decimal(required=True)
        category_id = graphene.ID(required=True)

    subcategory = graphene.Field(SubcategoryType)

    def mutate(self, info, name, percentage, category_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to create a subcategory")

        category = Category.objects.get(pk=category_id)
        if category.budget_plan.user != user:
            raise Exception("You can only add subcategories to your own categories")

        # Calculate total existing percentages for this category
        existing_total = Subcategory.objects.filter(category=category).aggregate(
            total=models.Sum('percentage'))['total'] or 0

        # Check if new total would exceed 100%
        new_total = existing_total + percentage
        if new_total > 100:
            raise Exception(f"Total percentage cannot exceed 100%. Current total: {existing_total}%")

        subcategory = Subcategory(
            name=name,
            percentage=percentage,
            category=category
        )
        subcategory.save()
        return CreateSubcategory(subcategory=subcategory)
    

class UpdateSubcategory(graphene.Mutation):
    class Arguments:
        subcategory_id = graphene.ID(required=True)
        name = graphene.String()
        percentage = graphene.Decimal()

    subcategory = graphene.Field(SubcategoryType)

    @staticmethod
    def validate_new_total(category, current_subcategory, new_percentage):
        total = Subcategory.objects.filter(category=category)\
        .exclude(id=current_subcategory.id)\
        .aggregate(total=models.Sum('percentage'))['total'] or 0
        return total + new_percentage <= 100

    @classmethod
    def mutate(cls, root, info, subcategory_id, name=None, percentage=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to update subcategory")

        subcategory = Subcategory.objects.get(pk=subcategory_id)
        if subcategory.category.budget_plan.user != user:
            raise Exception("You can only update subcategories in your own budget plans")

        if percentage:
            if not cls.validate_new_total(subcategory.category, subcategory, percentage):
                raise Exception("Total percentage cannot exceed 100%")
            subcategory.percentage = percentage

        if name:
            subcategory.name = name

        subcategory.save()
        return UpdateSubcategory(subcategory=subcategory)
 

class FinalizeBudgetPlan(graphene.Mutation):
    class Arguments:
        budget_plan_id = graphene.ID(required=True)
    
    budget_plan = graphene.Field(BudgetPlanType)
    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def validate_category_total(budget_plan):
        total = Category.objects.filter(budget_plan=budget_plan).aggregate(
            total=models.Sum('percentage'))['total'] or 0
        return total == 100

    @staticmethod
    def validate_subcategory_totals(budget_plan):
        categories = Category.objects.filter(budget_plan=budget_plan)
        for category in categories:
            total = Subcategory.objects.filter(category=category).aggregate(
                total=models.Sum('percentage'))['total'] or 0
            if total != 100 and total != 0:  # Allow categories without subcategories
                return False
        return True

    @classmethod
    def mutate(cls, root, info, budget_plan_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to finalize a budget plan")

        budget_plan = BudgetPlan.objects.get(pk=budget_plan_id)
        if budget_plan.user != user:
            raise Exception("You can only finalize your own budget plans")

        if not cls.validate_category_total(budget_plan):
            raise Exception("Category percentages must total exactly 100%")

        if not cls.validate_subcategory_totals(budget_plan):
            raise Exception("Subcategories within each category must total exactly 100%")

        return FinalizeBudgetPlan(
            budget_plan=budget_plan,
            success=True,
            message="Budget plan successfully finalized"
        )
    

class UpdateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        percentage = graphene.Decimal()
        category_id = graphene.ID(required=True)

    Category = graphene.Field(CategoryType)

    @staticmethod
    def validate_new_total(budget_plan, current_category, new_percentage):
        total = Category.objects.filter(budget_plan=budget_plan)\
        .exclude(id=current_category.id)\
        .aggregate(total=models.Sum('percentage'))['total'] or 0

        #check if total is more than 100%
        return total + new_percentage <= 100
    
    def validate_new_name(budget_plan, current_category, new_name):
        new_name = Category.objects.filter(budget_plan=budget_plan).exclude(id=current_category)

        if not new_name.is_alpha():
            return False
        
        return new_name
    
    @classmethod
    def mutate(cls, root, info, category_id, name=None, percentage=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to update category")

        category = Category.objects.get(pk=category_id)

        # Check if plan is predefined or belongs to User
        if category.budget_plan.is_predefined or category.budget_plan.user != user:
            raise Exception("you can only update category in your custom budget plan")
        if name:
            category.name = name
        if percentage:
            if not cls.validate_new_total(category.budget_plan,category, percentage):
                raise Exception("Total sum of categorys cannot exceed 100%")
            category.percentage = percentage

        category.save()
        return UpdateCategory(Category=category)



            


class Mutation(graphene.ObjectType):
    create_budget_plan = CreateBudgetPlan.Field()
    create_category = CreateCategory.Field()
    create_subcategory = CreateSubcategory.Field()
    finalize_budget_plan = FinalizeBudgetPlan.Field()
    update_category = UpdateCategory.Field()
    update_subcategory = UpdateSubcategory.Field()
