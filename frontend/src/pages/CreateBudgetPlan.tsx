import React, { useState } from 'react';
import { useMutation, gql, useApolloClient } from '@apollo/client';
import { useNavigate } from 'react-router-dom';

import { GET_USER_BUDGET_PLANS } from '../queries/budgetQueries';


// GraphQL mutation for creating a budget plan
const CREATE_BUDGET_PLAN = gql`
  mutation CreateBudgetPlan($name: String!, $isPredefined: Boolean!) {
    createBudgetPlan(name: $name, isPredefined: $isPredefined) {
      budgetPlan {
        id
        name
        isPredefined
        createdAt
      }
    }
  }
`;

const CreateBudgetPlan = () => {
  const [name, setName] = useState('');
  const [isPredefined, setIsPredefined] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Set up the mutation
  const client = useApolloClient();
  const [createBudgetPlan, { loading }] = useMutation(CREATE_BUDGET_PLAN, {
    onCompleted: (data) => {
      // Update the cache with the new budget plan
      const existingPlans = client.readQuery({
        query: GET_USER_BUDGET_PLANS
      });
      if (existingPlans) {
        client.writeQuery({
          query: GET_USER_BUDGET_PLANS,
          data: {
            userBudgetPlans: [
              ...existingPlans.userBudgetPlans,
              data.createBudgetPlan.budgetPlan
            ]
          }
        });
      }
      // Navigate to the dashboard after successful creation
      navigate('/dashboard');
    },
    onError: (error) => {
      setError(error.message);
    }
  });

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!name.trim()) {
      setError('Budget plan name is required');
      return;
    }
    
    // Submit the mutation
    createBudgetPlan({
      variables: {
        name,
        isPredefined
      }
    });
  };

  return (
    <div className="create-budget-container">
      <h1>Create New Budget Plan</h1>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Budget Plan Name</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={loading}
            placeholder="e.g., Monthly Budget, Vacation Savings"
          />
        </div>
        
        {/* Only show this option if the user is an admin - we'll implement this later */}
        {/* 
        <div className="form-group checkbox">
          <input
            type="checkbox"
            id="isPredefined"
            checked={isPredefined}
            onChange={(e) => setIsPredefined(e.target.checked)}
            disabled={loading}
          />
          <label htmlFor="isPredefined">Make this a predefined plan (admin only)</label>
        </div>
        */}
        
        <div className="form-actions">
          <button type="button" onClick={() => navigate('/dashboard')} disabled={loading}>
            Cancel
          </button>
          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Budget Plan'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateBudgetPlan;
