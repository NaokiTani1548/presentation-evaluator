import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import Index from './pages/Route';
import Review from './pages/Review';
import Log from './pages/Log';

const App: React.FC = () => {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Index />} />
                    <Route path="/review" element={<Review />} />
                    <Route path="/log" element={<Log />} />
                </Routes>
            </Layout>
        </Router>
    );
};

export default App;