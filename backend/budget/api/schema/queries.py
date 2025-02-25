import graphene
from .types import BudgetPlanType, CategoryType, SubcategoryType
from budgets.models import BudgetPlan, Category, Subcategory

class Query(graphene.ObjectType):
    all_budget_plans = graphene.List(BudgetPlanType)
    budget_plan = graphene.Field(BudgetPlanType, id=graphene.Int())

    def resolve_all_budget_plans(self, info):
        return BudgetPlan.objects.all()
    
    def resolve_budget_plan(self, info, id):
        return BudgetPlan.objects.get(pk=id)
