import re 
from decimal import Decimal
from django.db import models
from budgets.models import Category, Subcategory

def validate_name(name):
    if not re.search('[a-zA-Z]', name):
        raise Exception("Name must contain at least one Letter")
    
    if not name or name.isspace():
        raise Exception("Name cannot be empty")
    
    return True


def validate_percentage_value(percentage):
    """ Validates Inf=dividual percentage values """
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

