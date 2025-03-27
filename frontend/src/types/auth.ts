export interface User {
    id: number;
    username: string;
}

export interface AuthState {
    isAuthenticated: boolean;
    user: User | null;
    loading: boolean;
    error: string | null;
}

export interface LoginInput {
    username: string;
    password: string;
}

export interface RegisterInput {
    username: string;
    password: string;
    email: string;
}

export interface LoginResponse {
    tokenAuth: {
        token: string;
    };
}

export interface RegisterResponse {
    register: {
        user: User | null;
        message: string;
        success: boolean;
    };
}

