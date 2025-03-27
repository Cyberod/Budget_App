import { useState } from 'react';
import { useMutation, gql } from '@apollo/client';
import { LoginInput, LoginResponse } from '../../types/auth';
import { Link, useNavigate } from 'react-router-dom';


// Define the GraphQL mutation
const LOGIN = gql`
  mutation TokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      token
    }
  }
`;

const Login = () => {
  // State for form inputs
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  // State for error messages
  const [error, setError] = useState<string | null>(null);
  
  // Set up the mutation
  const [login, { loading }] = useMutation<{ tokenAuth: { token: string } }, { username: string; password: string }>(LOGIN, {
    onCompleted: (data) => {
      // Store the token in localStorage
      localStorage.setItem('token', data.tokenAuth.token);
      window.location.href = '/dashboard';
      

      console.log('Login successful! Redirecting...');
      
      // Navigates to Home page
      navigate('/');
    },
    onError: (error) => {
      setError(error.message);
    }
  });
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clear previous errors
    setError(null);
    
    // Validate inputs
    if (!username.trim()) {
      setError('Username is required');
      return;
    }
    
    if (!password) {
      setError('Password is required');
      return;
    }
    
    // Submit the login mutation
    login({ variables: { username, password } });
  };
  
  return (
    <div className="login-container">
      <h2>Login</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      
      <p>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </div>
  );
};

export default Login;
