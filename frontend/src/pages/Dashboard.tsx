import { useQuery, gql } from '@apollo/client';
import { Link } from 'react-router-dom';
import {logout} from '../utils/auth';
import { BudgetPlan } from '../types/budget';
import { useEffect } from 'react';


// GraphQL query to get user's budget plans
const GET_USER_BUDGET_PLANS =  gql`
    query {
    userBudgetPlans {
    id
    name
    isPredefined
    createdAt
    }
    }
`;

// type for the query response
interface userBudgetPlansData { 
    userBudgetPlans: BudgetPlan[];
}

const Dashboard = () => {
    // Execute the GraphQL query
    const {loading, error, data, refetch } = useQuery<userBudgetPlansData>(
        GET_USER_BUDGET_PLANS,
    {
        fetchPolicy: 'network-only', // Fetch from network instead of cache
        // Refetch when the component mounts
        onCompleted: () => {
            console.log('Data fetched!');
        }
    });

    useEffect(() => {
        refetch();
      }, [refetch]);

    // Handle Logout
    const handleLogout = () => {
        logout();
    };

    return (
        <div className='dashboard-container'>
            <div className='dashboard-header'>
                <h1>Your Budget Dashboard</h1>
                <button onClick={handleLogout} className='logout-button'>
                    Logout
                </button>
            </div>

            <div className="dashboard-content">
                {loading ? (
                    <p>Loading your budget plans....</p>
                ): error ? (
                    <p className="error-message">Error: {error.message}</p>
                ): (
                    <>
                        <div className="budget-plans-header">
                            <h2>Your Budget Plans</h2>
                            <Link to="/create-budget" className='create-button'>
                                Create New Plan
                            </Link>
                        </div>                  


                    {data?.userBudgetPlans?.length === 0 ? (
                        <p>You don't have any budget plans yet. Create your first one!</p>
                        ) : (
                        <div className="budget-plans-grid">
                            {data?.userBudgetPlans?.map((plan) => (
                            <div key={plan.id} className="budget-plan-card">
                                <h3>{plan.name}</h3>
                                <p>Created: {new Date(plan.createdAt).toLocaleDateString()}</p>
                                <p>{plan.isPredefined ? 'Predefined Plan' : 'Custom Plan'}</p>
                                <Link to={`/budget/${plan.id}`} className="view-button">
                                View Details
                                </Link>
                            </div>
                            ))}
                        </div>
                        )}
                    </>


                )}
            </div>

        </div>
    );
};

export default Dashboard;