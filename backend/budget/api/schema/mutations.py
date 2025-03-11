import graphene
from graphql_jwt.decorators import login_required
from django.db import models
from .types import BudgetPlanType, CategoryType, SubcategoryType
from budgets.models import BudgetPlan, Category, Subcategory
from .validators import (
    validate_name,
    validate_percentage_value,
    validate_category_total,
    validate_subcategory_total,
    validate_budget_plan_name_unique,
    validate_category_name_unique,
    validate_plan_completeness,
    validate_plan_status,
    validate_subcategory_name_unique
)


class CreateBudgetPlan(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        is_predefined = graphene.Boolean(default_value=False)

    budget_plan = graphene.Field(BudgetPlanType)

    @classmethod
    @login_required
    def mutate(cls, root, info, name, is_predefined=False):
        user = info.context.user
        validate_name(name)
        validate_budget_plan_name_unique(name, user, current_plan=None)
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
    

class UpdateBudgetPlan(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        budget_plan_id = graphene.ID(required=True)

    budget_plan = graphene.Field(BudgetPlanType)

    @classmethod
    @login_required
    def mutate(cls, root, info, budget_plan_id, name=None):
        user = info.context.user

        if not user.is_authenticated:
            raise Exception("You must be logged in to update budget plan")
        
        budget_plan = BudgetPlan.objects.get(pk=budget_plan_id)
        if budget_plan.user != user:
            raise Exception("You can only update your custom plans")
        
        if budget_plan.is_predefined:
            raise Exception("Predefined plans cannot be updated")
        
        if name:
            budget_plan.name = name
            validate_name(name)
            validate_budget_plan_name_unique(name, user, budget_plan)
            

        budget_plan.save()
        return UpdateBudgetPlan(budget_plan=budget_plan)


class DeleteBudgetPlan(graphene.Mutation):
    class Arguments:
        budget_plan_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    @login_required
    def mutate(cls, root, info, budget_plan_id, name=None):
        user = info.context.user

        if not user.is_authenticated:
            raise Exception("You must be logged in to delete budget plan")
        
        budget_plan = BudgetPlan.objects.get(pk=budget_plan_id)
        if budget_plan.user != user:
            raise Exception("You can only delete your custom plans")
        
        if budget_plan.is_predefined:
            raise Exception("Predefined plans cannot be deleted")
        
        

        budget_plan.delete()
        return DeleteBudgetPlan(
            success=True,
            message="Budget plan Successfully deleted"
        )


class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        percentage = graphene.Decimal(required=True)
        budget_plan_id = graphene.ID(required=True)

    Category = graphene.Field(CategoryType)

    @login_required
    def mutate(self, info, name, percentage, budget_plan_id):
        user = info.context.user
        validate_name(name)
        validate_percentage_value(percentage)

        budget_plan = BudgetPlan.objects.get(pk=budget_plan_id)
        validate_category_name_unique(name, budget_plan)
        
        if not user.is_authenticated:
            raise Exception("You must be logged in to create a category")
        
        validate_category_total(budget_plan, current_category=None, new_percentage=percentage)
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
    

    @classmethod
    @login_required
    def mutate(cls, root, info, category_id, name=None, percentage=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to update category")

        category = Category.objects.get(pk=category_id)

        # Check if plan is predefined or belongs to User
        if category.budget_plan.is_predefined or category.budget_plan.user != user:
            raise Exception("you can only update category in your custom budget plan")
        if name:
            validate_name(name)
            validate_category_name_unique(name, category.budget_plan, category)
            category.name = name
        if percentage:
            validate_percentage_value(percentage)
            validate_category_total(category.budget_plan, category, percentage)
            category.percentage = percentage

        category.save()
        return UpdateCategory(Category=category)
    

class DeleteCategory(graphene.Mutation):
    class Arguments:
        category_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    @login_required
    def mutate(cls, root, info, category_id):
        user = info.context.user

        if not user.is_authenticated:
            raise Exception("You must be logged in to delete category")
        
        category = Category.objects.get(pk=category_id)

        if category.budget_plan.user != user:
            raise Exception("You can only delete categories from your own budget plans")
        
        if category.budget_plan.is_predefined:
            raise Exception("you can only update category in your custom budget plan")
        
        

        category.delete()
        return DeleteCategory(
            success=True,
            message="Category Successfully deleted"
        )

class CreateSubcategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        percentage = graphene.Decimal(required=True)
        category_id = graphene.ID(required=True)

    subcategory = graphene.Field(SubcategoryType)

    @login_required
    def mutate(self, info, name, percentage, category_id):

        user = info.context.user
        validate_name(name)
        validate_percentage_value(percentage)

        category = Category.objects.get(pk=category_id)
        validate_subcategory_name_unique(name, category)
        
        if not user.is_authenticated:
            raise Exception("You must be logged in to create a subcategory")

        
        validate_subcategory_total(category, current_subcategory=None, new_percentage=percentage)
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
    @login_required
    def mutate(cls, root, info, subcategory_id, name=None, percentage=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to update subcategory")

        
        subcategory = Subcategory.objects.get(pk=subcategory_id)
        if subcategory.category.budget_plan.user != user:
            raise Exception("You can only update subcategories in your own budget plans")

        if percentage:
            validate_percentage_value(percentage)
            validate_subcategory_total(subcategory.category, subcategory, percentage)
            subcategory.percentage = percentage

        if name:
            validate_name(name)
            validate_subcategory_name_unique(name, subcategory.category, subcategory)
            subcategory.name = name

        subcategory.save()
        return UpdateSubcategory(subcategory=subcategory)
 

class DeleteSubcategory(graphene.Mutation):
    class Arguments:
        subcategory_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    @login_required
    def mutate(cls, root,  info, subcategory_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to delete a subcategory")

        subcategory = Subcategory.objects.get(pk=subcategory_id)
        
        if subcategory.category.budget_plan.user != user:
            raise Exception("You can only delete subcategories from your own budget plans")
            
        if subcategory.category.budget_plan.is_predefined:
            raise Exception("Subcategories in predefined plans cannot be deleted")

        subcategory.delete()
        return DeleteSubcategory(
            success=True, 
            message="Subcategory successfully deleted"
        )

class FinalizeBudgetPlan(graphene.Mutation):
    class Arguments:
        budget_plan_id = graphene.ID(required=True)
    
    budget_plan = graphene.Field(BudgetPlanType)
    success = graphene.Boolean()
    message = graphene.String()


    @classmethod
    @login_required
    def mutate(cls, root, info, budget_plan_id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("You must be logged in to finalize a budget plan")

        budget_plan = BudgetPlan.objects.get(pk=budget_plan_id)
        if budget_plan.user != user:
            raise Exception("You can only finalize your own budget plans")

        validate_plan_status(budget_plan)
        validate_plan_completeness(budget_plan)

        categories = Category.objects.filter(budget_plan=budget_plan)
        for category in categories:
            subcategories = Subcategory.objects.filter(category=category)
            if subcategories.exists():
                validate_subcategory_total(category, current_subcategory=None, new_percentage=None)

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
    update_category = UpdateCategory.Field()
    update_subcategory = UpdateSubcategory.Field()
    update_budget_plan = UpdateBudgetPlan.Field()
    delete_budget_plan = DeleteBudgetPlan.Field()
    delete_category = DeleteCategory.Field()
    delete_subcategory = DeleteSubcategory.Field()

