from graphene_django import DjangoObjectType
from budgets.models import BudgetPlan, Category, Subcategory
#from django.contrib.auth.models import User

from django.contrib.auth import get_user_model


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username')


class BudgetPlanType(DjangoObjectType):
    class Meta:
        model = BudgetPlan
        fields = ('id', 'name', 'user', 'is_predefined', 'created_at', 'category_set', 'subcategory_set')

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class SubcategoryType(DjangoObjectType):
    class Meta:
        model = Subcategory