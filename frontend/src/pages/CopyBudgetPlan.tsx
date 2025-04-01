import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, gql } from '@apollo/client';

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

// GraphQL mutation to update a category
const UPDATE_CATEGORY = gql`
  mutation UpdateCategory($categoryId: ID!, $name: String, $percentage: Decimal) {
    updateCategory(categoryId: $categoryId, name: $name, percentage: $percentage) {
      Category {
        id
        name
        percentage
      }
    }
  }
`;

// GraphQL mutation to delete a category
const DELETE_CATEGORY = gql`
  mutation DeleteCategory($categoryId: ID!) {
    deleteCategory(categoryId: $categoryId) {
      success
      message
    }
  }
`;

// Category form state type
interface CategoryFormState {
  id?: string;
  name: string;
  percentage: string;
  isEditing: boolean;
}

const BudgetPlanDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // State for the category form
  const [categoryForm, setCategoryForm] = useState<CategoryFormState>({
    name: '',
    percentage: '',
    isEditing: false
  });
  
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState<string | null>(null);
  
  // Execute the query to get the budget plan details
  const { loading, error: queryError, data, refetch } = useQuery(
    GET_BUDGET_PLAN,
    {
      variables: { id },
      fetchPolicy: 'network-only', // Don't use cache
    }
  );
  
  // Debug: Log the data when it changes
  useEffect(() => {
    if (data) {
      console.log('GraphQL response:', data);
    }
  }, [data]);
  
  // Set up the mutation to create a category
  const [createCategory, { loading: creatingCategory }] = useMutation(CREATE_CATEGORY, {
    onCompleted: () => {
      resetForm();
      refetch();
    },
    onError: (error) => {
      setError(error.message);
    }
  });
  
  // Set up the mutation to update a category
  const [updateCategory, { loading: updatingCategory }] = useMutation(UPDATE_CATEGORY, {
    onCompleted: () => {
      resetForm();
      refetch();
    },
    onError: (error) => {
      setError(error.message);
    }
  });
  
  // Set up the mutation to delete a category
  const [deleteCategory, { loading: deletingCategory }] = useMutation(DELETE_CATEGORY, {
    onCompleted: () => {
      setDeleteConfirmation(null);
      refetch();
    },
    onError: (error) => {
      setError(error.message);
    }
  });
  
  // Reset the form
  const resetForm = () => {
    setCategoryForm({
      name: '',
      percentage: '',
      isEditing: false
    });
    setShowCategoryForm(false);
    setError(null);
  };
  
  // Handle form submission for creating/updating a category
  const handleSubmitCategory = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!categoryForm.name.trim()) {
      setError('Category name is required');
      return;
    }
    
    const percentage = parseFloat(categoryForm.percentage);
    if (isNaN(percentage) || percentage <= 0 || percentage > 100) {
      setError('Percentage must be a number between 0 and 100');
      return;
    }
    
    // Check if data exists
    if (!data) {
      console.error('Data is undefined');
      setError('Data is not available. Please try again.');
      return;
    }
    
    // Check if budgetPlan exists
    if (!data.budgetPlan) {
      console.error('budgetPlan is undefined');
      setError('Budget plan data is not available. Please try again.');
      return;
    }
    
    // Check if categorySet exists
    if (!Array.isArray(data.budgetPlan.categorySet)) {
      console.error('categorySet is not an array:', data.budgetPlan.categorySet);
      setError('Category data is not available. Please try again.');
      return;
    }
    
    if (categoryForm.isEditing && categoryForm.id) {
      const currentCategory = data.budgetPlan.categorySet.find(
        (cat: any) => cat.id === categoryForm.id
      );
      
      if (currentCategory) {
        const otherCategoriesTotal = data.budgetPlan.categorySet
          .filter((cat: any) => cat.id !== categoryForm.id)
          .reduce((sum: number, cat: any) => sum + parseFloat(cat.percentage), 0);
        
        const newTotal = otherCategoriesTotal + percentage;
        
        if (newTotal > 100) {
          setError(`Total percentage would exceed 100%. Other categories total: ${otherCategoriesTotal.toFixed(2)}%, new total would be: ${newTotal.toFixed(2)}%`);
          return;
        }
      }
      
      // Update existing category
      updateCategory({
        variables: {
          categoryId: categoryForm.id,
          name: categoryForm.name,
          percentage: categoryForm.percentage
        }
      });
    } else {
      // For new categories, check if adding this would exceed 100%
      const currentTotal = data.budgetPlan.categorySet.reduce(
        (sum: number, cat: any) => sum + parseFloat(cat.percentage), 
        0
      );
      
      if (currentTotal + percentage > 100) {
        setError(`Adding this category would exceed 100%. Current total: ${currentTotal.toFixed(2)}%, new total would be: ${(currentTotal + percentage).toFixed(2)}%`);
        return;
      }
      
      // Create new category
      createCategory({
        variables: {
          name: categoryForm.name,
          percentage: categoryForm.percentage,
          budgetPlanId: id
        }
      });
    }
  };
  
  // Handle edit category button click
  const handleEditCategory = (category: { id: string; name: string; percentage: string }) => {
    setCategoryForm({
      id: category.id,
      name: category.name,
      percentage: category.percentage,
      isEditing: true
    });
    setShowCategoryForm(true);
    setError(null);
  };
  
  // Handle delete category button click
  const handleDeleteCategory = (categoryId: string) => {
    setDeleteConfirmation(categoryId);
  };
  
  // Confirm category deletion
  const confirmDeleteCategory = () => {
    if (deleteConfirmation) {
      deleteCategory({
        variables: {
          categoryId: deleteConfirmation
        }
      });
    }
  };
  
  // Calculate the total percentage of all categories
  const totalPercentage = data?.budgetPlan?.categorySet?.reduce(
    (sum: number, category: any) => sum + parseFloat(category.percentage),
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
        <p>Total Allocation: {totalPercentage.toFixed(2)}%</p>
        <p>Remaining: {(100 - totalPercentage).toFixed(2)}%</p>
      </div>
      
      <div className="categories-section">
        <div className="categories-header">
          <h2>Categories</h2>
          {!data.budgetPlan.isPredefined && (
            <button 
              onClick={() => {
                resetForm();
                setShowCategoryForm(!showCategoryForm);
              }}
              className="add-button"
            >
              {showCategoryForm ? 'Cancel' : 'Add Category'}
            </button>
          )}
        </div>
        
        {showCategoryForm && (
          <div className="category-form">
            <h3>{categoryForm.isEditing ? 'Edit Category' : 'Add New Category'}</h3>
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmitCategory}>
              <div className="form-group">
                <label htmlFor="categoryName">Category Name</label>
                <input
                  type="text"
                  id="categoryName"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})}
                  disabled={creatingCategory || updatingCategory}
                  placeholder="e.g., Housing, Food, Transportation"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="categoryPercentage">Percentage (%)</label>
                <input
                  type="number"
                  id="categoryPercentage"
                  value={categoryForm.percentage}
                  onChange={(e) => setCategoryForm({...categoryForm, percentage: e.target.value})}
                  disabled={creatingCategory || updatingCategory}
                  placeholder="e.g., 30"
                  min="0.01"
                  max="100"
                  step="0.01"
                />
              </div>
              
              <div className="form-actions">
                <button 
                  type="button" 
                  onClick={resetForm}
                  disabled={creatingCategory || updatingCategory}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={creatingCategory || updatingCategory}
                >
                  {creatingCategory || updatingCategory 
                    ? (categoryForm.isEditing ? 'Updating...' : 'Adding...') 
                    : (categoryForm.isEditing ? 'Update Category' : 'Add Category')}
                </button>
              </div>
            </form>
          </div>
        )}
        
        {/* Delete confirmation modal */}
        {deleteConfirmation && (
          <div className="delete-confirmation-modal">
            <div className="modal-content">
              <h3>Confirm Deletion</h3>
              <p>Are you sure you want to delete this category? This action cannot be undone.</p>
              <div className="modal-actions">
                <button 
                  onClick={() => setDeleteConfirmation(null)}
                  disabled={deletingCategory}
                >
                  Cancel
                </button>
                <button 
                  onClick={confirmDeleteCategory}
                  disabled={deletingCategory}
                  className="delete-button"
                >
                  {deletingCategory ? 'Deleting...' : 'Delete Category'}
                </button>
              </div>
            </div>
          </div>
        )}
        
        {data.budgetPlan.categorySet.length === 0 ? (
          <p>No categories yet. Add some to start building your budget plan.</p>
        ) : (
          <div className="categories-list">
            {data.budgetPlan.categorySet.map((category: any) => (
              <div key={category.id} className="category-card">
                <div className="category-info">
                  <h3>{category.name}</h3>
                  <p>{parseFloat(category.percentage).toFixed(2)}%</p>
                </div>
                {!data.budgetPlan.isPredefined && (
                  <div className="category-actions">
                    <button 
                      className="edit-button"
                      onClick={() => handleEditCategory(category)}
                    >
                      Edit
                    </button>
                    <button 
                      className="delete-button"
                      onClick={() => handleDeleteCategory(category.id)}
                    >
                      Delete
                    </button>
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
