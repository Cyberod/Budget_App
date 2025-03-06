import re 
from decimal import Decimal
from django.db import models
from budgets.models import Category, Subcategory, BudgetPlan



## Logic for validation of Plan names and completeness
def validate_name(name):
    """ Validates Budget plan, categories and subcategories names """

    # Must contain letters, can include numbers and spaces
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9\s]*$', name):
        raise Exception("Plan name must start with a letter \
                        and contain only letters, numbers, and spaces")
    
    # Must contain a name
    if not name or name.isspace():
        raise Exception("Name cannot be empty")
    
    # Must be 3-50 characters long
    if len(name) < 3 or len(name) > 50:
        raise Exception("Plan name must be between 3 to 50 characters")
    
    
    return True

def validate_budget_plan_name_unique(name, user, current_plan=None):
    """Validates budget plan name is unique for this user"""
    query = BudgetPlan.objects.filter(user=user, name=name)
    if current_plan:
        query = query.exclude(id=current_plan.id)
    if query.exists():
        raise Exception(f"You already have a budget plan named '{name}'")
    return True
    

def validate_category_name_unique(name, budget_plan, current_category=None):
    """Validates category name is unique within this budget plan"""
    query = Category.objects.filter(budget_plan=budget_plan, name=name)
    if current_category:
        query.exclude(id=current_category.id)
    if query.exists():
        raise Exception(f"This budget plan already has a category named '{name}'")
    return True

def validate_subcategory_name_unique(name, category, current_subcategory=None):
    """Validates subcategory name is unique within this category"""
    query = Subcategory.objects.filter(category=category, name=name)
    if current_subcategory:
        query = query.exclude(id=current_subcategory.id)
    if query.exists():
        raise Exception(f"This category already has a subcategory named '{name}'")
    return True


def validate_plan_completeness(budget_plan):
    """ Validates if budget plan is complete and ready for Finalization """

    # Must have at least one category
    categories = Category.objects.filter(budget_plan=budget_plan)

    if not categories.exists():
        raise Exception("Budget Plan must have at least one Category")
    
    # categories must total 100%
    total = categories.aggregate(total=models.Sum('percentage'))['total'] or 0
    if total != 100:
        raise Exception("Category percentages must total 100%. Current total: {total}%")
    
    return True

def validate_plan_status(budget_plan):
    """ Validates budget plans status for operation """
    if budget_plan.is_predefined:
        raise Exception("Cannot modify predefined budget plans")
    return True




## Logics for validation of Percentages and Decimal Places
def validate_percentage_value(percentage):
    """ Validates Individual percentage values """
    if not isinstance(percentage, Decimal):
        percentage = Decimal(str(percentage))

    if percentage <= 0:
        raise Exception("Percentage must be greater than zero")

    if percentage > 100:
        raise Exception("Percentage cannot exceed 100")

    if percentage.as_tuple().exponent < -2:
        raise Exception("Percentage can only have 2 decimal places")

    return True



def validate_cateogry_total(budget_plan, current_category=None, new_percentage=None):
    """ Validates total percentage for categories in a Budget plan """

    query = Category.objects.filter(budget_plan=budget_plan)

    if current_category:
        query = query.exclude(id=current_category.id)

    total = query.aggregate(total=models.Sum('percentage'))['total'] or 0

    if new_percentage:
        total += Decimal(str(new_percentage))

    return True


def validate_subcategory_total(category, current_subcategory, new_percentage):
    """ Validates total percentage of subcategories in a category """

    query = Subcategory.objects.filter(category=category)

    if current_subcategory:
        query = query.exclude(id = current_subcategory.id)

    total = query.aggregate(total=models.Sum('percentage'))['total'] or 0

    if new_percentage:
        total += Decimal(str(new_percentage))

    return True

