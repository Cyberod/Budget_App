import graphene
from graphql_jwt.decorators import login_required
from .types import BudgetPlanType, CategoryType, SubcategoryType, CurrencyType
from budgets.models import BudgetPlan, Category, Subcategory, Currency
from django.db import models
from api.services.currency_converter import CurrencyConverter

class Query(graphene.ObjectType):
    all_budget_plans = graphene.List(BudgetPlanType)
    budget_plan = graphene.Field(BudgetPlanType, id=graphene.ID())
    user_budget_plans = graphene.List(BudgetPlanType)
    predefined_plans = graphene.List(BudgetPlanType)

    all_currencies = graphene.List(CurrencyType)
    convert_currency = graphene.Field(
        graphene.Decimal,
        amount=graphene.Decimal(required=True),
        from_currency=graphene.String(required=True),
        to_currency=graphene.String(required=True)
    )


    @login_required
    def resolve_all_budget_plans(self, info):
        user = info.context.user

        if not user.is_authenticated:
            return BudgetPlan.objects.filter(is_predefined=True)
        return BudgetPlan.objects.filter(
            models.Q(is_predefined=True) | models.Q(user=user)
        )
    
    @login_required
    def resolve_budget_plan(self, info, id):
        user = info.context.user

        budget_plan = BudgetPlan.objects.get(pk=id)
        # The budget plan has to be predefined and
        if budget_plan.is_predefined or (user.is_authenticated and budget_plan.user == user):
            return budget_plan
        
        raise Exception("you do not have permission to view this budget plan")
    
    @login_required
    def resolve_user_budget_plan(self, info, id):
        user = info.context.user

        if user.is_authenticated:
            return BudgetPlan.objects.filter(user=user, is_predefined=False)
        
    def resolve_predefined_plans(self, info):
        return BudgetPlan.ojects.filter(is_predefined=True)

    def resolve_all_currencies(self, info):
        return Currency.objects.all()
        
    def resolve_convert_currency(self, info, amount, from_currency, to_currency):
        return CurrencyConverter.convert(amount, from_currency, to_currency)