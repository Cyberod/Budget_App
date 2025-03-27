export interface BudgetPlan {
    id: string;
    name: string;
    isPredefined: boolean;
    createdAt: string;
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
  