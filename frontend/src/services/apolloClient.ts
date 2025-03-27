import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

// Creates a link to my GrapgQL API
const httpLink = createHttpLink({
    uri: 'http://localhost:8000/graphql/',
});

// Adds the token to the request headers
const authLink = setContext((_, { headers }) => {
    // Get the token from the local storage if it exists
    const token = localStorage.getItem('token');

    // Returns the headers to the context so httpLink can read them
    return {
        headers: {
            ...headers,
            authorization: token ? `JWT ${token}` : '',
        }
    };
});

// Creates the Apollo client
const client = new ApolloClient({
    link: authLink.concat(httpLink),
    cache: new InMemoryCache()
});

export default client;