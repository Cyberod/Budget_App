export interface BudgetPlan {
    id: string;
    name: string;
    isPredefined: boolean;
    createdAt: string;
    categorySet?: Array<{
    id: string;
    name: string;
    percentage: string;
    }>;
  }
  
  export interface Category {
    id: string;
    name: string;
    percentage: number;
    budgetPlan: string; // ID of the budget plan
  }
  
  export interface Subcategory {
    id: string;
    name: string;
    percentage: number;
    category: string; // ID of the category
  }

// Define the type for the query response
export interface BudgetPlanDetailData {
  budgetPlan: BudgetPlan & {
    categorySet: {
      id: string;
      name: string;
      percentage: number;
    }[];
  };
}

export interface BudgetPlanData {
  budgetPlan: BudgetPlan;
}

// Category form state type
export interface CategoryFormState {
  id?: string;
  name: string;
  percentage: string;
  isEditing: boolean;
}
  