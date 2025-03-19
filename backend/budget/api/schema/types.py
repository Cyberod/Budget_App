from graphene_django import DjangoObjectType
from budgets.models import BudgetPlan, Category, Subcategory
from budgets.models import Currency



from django.contrib.auth import get_user_model


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username')


class BudgetPlanType(DjangoObjectType):
    class Meta:
        model = BudgetPlan
        fields = ('id', 'name', 'user', 'is_predefined', 'created_at', 'category_set', 'currency')

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class SubcategoryType(DjangoObjectType):
    class Meta:
        model = Subcategory

class CurrencyType(DjangoObjectType):
    class Meta:
        model = Currency
        fields = ('code', 'name', 'symbol')