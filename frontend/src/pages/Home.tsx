const Home = () => {
    return (
        <div className="home-container">
            <h1>Welcome to Budget App</h1>
            <p> Your Personal Budget Planning tool</p>

            <div className="cta-buttons">
                <a href="/login" className="btn btn-primary">Login</a>
                <a href="/register" className="btn btn-secondary">Register</a>
            </div>
        </div>
    );
};

export default Home;