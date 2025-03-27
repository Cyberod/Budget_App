// Create a new file: src/pages/CopyBudgetPlan.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, gql } from '@apollo/client';
import { BudgetPlan } from '../types/budget';

// Query to get the predefined plan details
const GET_BUDGET_PLAN = gql`
  query GetBudgetPlan($id: ID!) {
    budgetPlan(id: $id) {
      id
      name
      isPredefined
    }
  }
`;

// Mutation to copy a predefined plan
const COPY_BUDGET_PLAN = gql`
  mutation CopyBudgetPlan($sourcePlanId: ID!, $name: String!) {
    copyBudgetPlan(sourcePlanId: $sourcePlanId, name: $name) {
      budgetPlan {
        id
        name
        isPredefined
        createdAt
      }
      success
      message
    }
  }
`;

interface BudgetPlanData {
  budgetPlan: BudgetPlan;
}

const CopyBudgetPlan = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Fetch the predefined plan details
  const { loading: loadingPlan, error: planError, data } = useQuery<BudgetPlanData>(
    GET_BUDGET_PLAN,
    {
      variables: { id },
      onCompleted: (data) => {
        // Set a default name for the copied plan
        setName(`Copy of ${data.budgetPlan.name}`);
      }
    }
  );

  // Set up the copy mutation
  const [copyBudgetPlan, { loading: copying }] = useMutation(COPY_BUDGET_PLAN, {
    onCompleted: (data) => {
      // Navigate to the new plan's detail page
      navigate(`/budget/${data.copyBudgetPlan.budgetPlan.id}`);
    },
    onError: (error) => {
      setError(error.message);
    }
  });

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('Please provide a name for your new budget plan');
      return;
    }
    
    copyBudgetPlan({
      variables: {
        sourcePlanId: id,
        name
      }
    });
  };

  if (loadingPlan) return <p>Loading plan details...</p>;
  if (planError) return <p>Error: {planError.message}</p>;
  if (!data?.budgetPlan) return <p>Plan not found</p>;
  if (!data.budgetPlan.isPredefined) {
    // Redirect if not a predefined plan
    navigate('/dashboard');
    return null;
  }

  return (
    <div className="copy-budget-container">
      <h1>Create Your Plan from Template</h1>
      <p>You're creating a new budget plan based on the "{data.budgetPlan.name}" template.</p>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Name for your new budget plan:</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={copying}
          />
        </div>
        
        <div className="form-actions">
          <button 
            type="button" 
            onClick={() => navigate('/dashboard')} 
            disabled={copying}
          >
            Cancel
          </button>
          <button type="submit" disabled={copying}>
            {copying ? 'Creating...' : 'Create My Plan'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CopyBudgetPlan;
