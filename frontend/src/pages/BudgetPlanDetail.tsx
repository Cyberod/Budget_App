import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, gql } from '@apollo/client';
import { BudgetPlan } from '../types/budget';

// GraphQL query to get a specific budget plan with its categories
const GET_BUDGET_PLAN = gql`
  query GetBudgetPlan($id: ID!) {
    budgetPlan(id: $id) {
      id
      name
      isPredefined
      createdAt
      categorySet {
        id
        name
        percentage
      }
    }
  }
`;

// GraphQL mutation to create a category
const CREATE_CATEGORY = gql`
  mutation CreateCategory($name: String!, $percentage: Decimal!, $budgetPlanId: ID!) {
    createCategory(name: $name, percentage: $percentage, budgetPlanId: $budgetPlanId) {
      Category {
        id
        name
        percentage
      }
    }
  }
`;

// Define the type for the query response
interface BudgetPlanDetailData {
  budgetPlan: BudgetPlan & {
    categorySet: {
      id: string;
      name: string;
      percentage: number;
    }[];
  };
}

const BudgetPlanDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // State for the new category form
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryPercentage, setNewCategoryPercentage] = useState('');
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Execute the query to get the budget plan details
  const { loading, error: queryError, data, refetch } = useQuery<BudgetPlanDetailData>(
    GET_BUDGET_PLAN,
    {
      variables: { id: id },
      fetchPolicy: 'network-only', // Don't use cache
    }
  );
  
  // Set up the mutation to create a category
  const [createCategory, { loading: creatingCategory }] = useMutation(CREATE_CATEGORY, {
    onCompleted: () => {
      // Clear the form and hide it
      setNewCategoryName('');
      setNewCategoryPercentage('');
      setShowCategoryForm(false);
      setError(null);
      
      // Refetch the budget plan to get the updated categories
      refetch();
    },
    onError: (error) => {
      setError(error.message);
    }
  });
  
  // Handle form submission for creating a new category
  const handleCreateCategory = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!newCategoryName.trim()) {
      setError('Category name is required');
      return;
    }
    
    const percentage = parseFloat(newCategoryPercentage);
    if (isNaN(percentage) || percentage <= 0 || percentage > 100) {
      setError('Percentage must be a number between 0 and 100');
      return;
    }
    
    // Submit the mutation
    createCategory({
      variables: {
        name: newCategoryName,
        percentage: newCategoryPercentage,
        budgetPlanId: id
      }
    });
  };

  console.log("Mutation variables:", {
    name: newCategoryName,
    percentage: newCategoryPercentage,
    budgetPlanId: id
  });
  
  
  // Calculate the total percentage of all categories
  const totalPercentage = data?.budgetPlan.categorySet.reduce(
    (sum, category) => sum + category.percentage,
    0
  ) || 0;
  
  // Handle loading and error states
  if (loading) return <p>Loading budget plan details...</p>;
  if (queryError) return <p>Error: {queryError.message}</p>;
  if (!data?.budgetPlan) return <p>Budget plan not found</p>;
  
  return (
    <div className="budget-plan-detail">
      <div className="budget-plan-header">
        <h1>{data.budgetPlan.name}</h1>
        <button onClick={() => navigate('/dashboard')} className="back-button">
          Back to Dashboard
        </button>
      </div>
      
      <div className="budget-plan-info">
        <p>Created: {new Date(data.budgetPlan.createdAt).toLocaleDateString()}</p>
        <p>Type: {data.budgetPlan.isPredefined ? 'Predefined Plan' : 'Custom Plan'}</p>
        <p>Total Allocation: {totalPercentage}%</p>
        <p>Remaining: {(100 - totalPercentage)}%</p>
      </div>
      
      <div className="categories-section">
        <div className="categories-header">
          <h2>Categories</h2>
          {!data.budgetPlan.isPredefined && (
            <button 
              onClick={() => setShowCategoryForm(!showCategoryForm)}
              className="add-button"
            >
              {showCategoryForm ? 'Cancel' : 'Add Category'}
            </button>
          )}
        </div>
        
        {showCategoryForm && (
          <div className="category-form">
            <h3>Add New Category</h3>
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
            
            <form onSubmit={handleCreateCategory}>
              <div className="form-group">
                <label htmlFor="categoryName">Category Name</label>
                <input
                  type="text"
                  id="categoryName"
                  value={newCategoryName}
                  onChange={(e) => setNewCategoryName(e.target.value)}
                  disabled={creatingCategory}
                  placeholder="e.g., Housing, Food, Transportation"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="categoryPercentage">Percentage (%)</label>
                <input
                  type="number"
                  id="categoryPercentage"
                  value={newCategoryPercentage}
                  onChange={(e) => setNewCategoryPercentage(e.target.value)}
                  disabled={creatingCategory}
                  placeholder="e.g., 30"
                  min="0.01"
                  max="100"
                  step="0.01"
                />
              </div>
              
              <div className="form-actions">
                <button type="submit" disabled={creatingCategory}>
                  {creatingCategory ? 'Adding...' : 'Add Category'}
                </button>
              </div>
            </form>
          </div>
        )}
        
        {data.budgetPlan.categorySet.length === 0 ? (
          <p>No categories yet. Add some to start building your budget plan.</p>
        ) : (
          <div className="categories-list">
            {data.budgetPlan.categorySet.map((category) => (
              <div key={category.id} className="category-card">
                <div className="category-info">
                  <h3>{category.name}</h3>
                  <p>{category.percentage}%</p>
                </div>
                {!data.budgetPlan.isPredefined && (
                  <div className="category-actions">
                    <button className="edit-button">Edit</button>
                    <button className="delete-button">Delete</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BudgetPlanDetail;
