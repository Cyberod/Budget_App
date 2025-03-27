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