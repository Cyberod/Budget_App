import graphene
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
            raise Exception ("You must be logged in to create a category")
        
        budget_plan = BudgetPlan.objects.get(pk=budget_plan_id)
        if budget_plan.user != user:
            raise Exception("You can only add categories to your own budget plans")
        
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

        subcategory = Subcategory(
            name=name,
            percentage=percentage,
            category=category
        )
        subcategory.save()
        return CreateSubcategory(subcategory=subcategory)
    


class Mutation(graphene.ObjectType):
    create_budget_plan = CreateBudgetPlan.Field()
    create_category = CreateCategory.Field()
    create_subcategory = CreateSubcategory.Field()