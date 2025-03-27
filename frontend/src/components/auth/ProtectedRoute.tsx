import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../../utils/auth';
import  { JSX } from 'react';

interface ProtectedRouteProps {
    children: JSX.Element;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
    if (!isAuthenticated()) {
        // Redirects to login if not Authenticaed
        return <Navigate to="/login"/>;
    }

    return children;
}

export default ProtectedRoute;