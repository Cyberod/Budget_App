from graphene_django import DjangoObjectType
from budgets.models import BudgetPlan, Category, Subcategory


class BudgetPlanType(DjangoObjectType):
    class Meta:
        model = BudgetPlan
        fields = ('id', 'name', 'user', 'is_predefined', 'created_at')

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class SubcategoryType(DjangoObjectType):
    class Meta:
        model = Subcategory