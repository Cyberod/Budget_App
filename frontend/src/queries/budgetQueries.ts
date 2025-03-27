import { gql } from '@apollo/client';

export const GET_USER_BUDGET_PLANS = gql`
  query GetUserBudgetPlans {
    userBudgetPlans {
      id
      name
      isPredefined
      createdAt
    }
  }
`;
