import { ApolloProvider } from '@apollo/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import client from './services/apolloClient';
import Home from './pages/Home';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Dashboard from './pages/Dashboard';
import CreateBudgetPlan from './pages/CreateBudgetPlan';
import BudgetPlanDetail from './pages/BudgetPlanDetail';
import ProtectedRoute from './components/auth/ProtectedRoute';
import CopyBudgetPlan from './pages/CopyBudgetPlan';

import './styles/App.css';

function App() {
  return (
    <ApolloProvider client={client}>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/create-budget" 
              element={
                <ProtectedRoute>
                  <CreateBudgetPlan />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/budget/:id" 
              element={
                <ProtectedRoute>
                  <BudgetPlanDetail />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/budget/:id" 
              element={
                <ProtectedRoute>
                  <BudgetPlanDetail />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/copy-budget/:id" 
              element={
                <ProtectedRoute>
                  <CopyBudgetPlan />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </div>
      </Router>
    </ApolloProvider>
  );
}

export default App;
