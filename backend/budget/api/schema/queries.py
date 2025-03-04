import graphene
from .types import BudgetPlanType, CategoryType, SubcategoryType
from budgets.models import BudgetPlan, Category, Subcategory
from django.db import models

class Query(graphene.ObjectType):
    all_budget_plans = graphene.List(BudgetPlanType)
    budget_plan = graphene.Field(BudgetPlanType, id=graphene.Int())
    user_budget_plans = graphene.List(BudgetPlanType)
    predefined_plans = graphene.List(BudgetPlanType)

    def resolve_all_budget_plans(self, info):
        user = info.context.user

        if not user.is_authenticated:
            return BudgetPlan.objects.filter(is_predefined=True)
        return BudgetPlan.objects.filter(
            models.Q(is_predefined=True) | models.Q(user=user)
        )
    
    def resolve_budget_plan(self, info, id):
        user = info.context.user

        budget_plan = BudgetPlan.objects.get(pk=id)
        # The budget plan has to be predefined and
        if budget_plan.is_predefined or (user.is_authenticated and budget_plan.user == user):
            return budget_plan
        
        raise Exception("you do not have permission to view this budget plan")
    
    def resolve_user_budget_plan(self, info, id):
        user = info.context.user

        if user.is_authenticated:
            return BudgetPlan.objects.filter(user=user, is_predefined=False)
        
    def resolve_predefined_plans(self, info):
        return BudgetPlan.ojects.filter(is_predefined=True)
