import graphene
from django.db import models
from .types import BudgetPlanType, CategoryType, SubcategoryType
from budgets.models import BudgetPlan, Category, Subcategory


class CreateBudgetPlan(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        is_predefined = graphene.Boolean(default_value=False)

    budget_plan = graphene.Field(BudgetPlanType)

    def mutate(self, info, name, is_predefined):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to create a Budget plan")
        
        budget_plan = BudgetPlan(
            name = name,
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



class Mutation(graphene.ObjectType):
    create_budget_plan = CreateBudgetPlan.Field()
    create_category = CreateCategory.Field()
    create_subcategory = CreateSubcategory.Field()
    finalize_budget_plan = FinalizeBudgetPlan.Field()
