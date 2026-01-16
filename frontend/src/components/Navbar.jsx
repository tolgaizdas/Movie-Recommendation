import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
    const { currentUser, logout } = useAuth();
    const navigate = useNavigate();

    async function handleLogout() {
        try {
            await logout();
            navigate('/login');
        } catch {
            console.error("Failed to log out");
        }
    }

    return (
        <nav className="bg-gray-800 p-4 shadow-md">
            <div className="container mx-auto flex justify-between items-center">
                <Link to="/" className="text-xl font-bold text-red-500">
                    MovieRec
                </Link>
                <div className="space-x-4">
                    {currentUser ? (
                        <>
                            <Link to="/" className="text-gray-300 hover:text-white">Home</Link>
                            <Link to="/recommendations" className="text-gray-300 hover:text-white">Recommendations</Link>
                            <button
                                onClick={handleLogout}
                                className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded"
                            >
                                Logout
                            </button>
                        </>
                    ) : (
                        <Link to="/login" className="text-gray-300 hover:text-white">Login</Link>
                    )}
                </div>
            </div>
        </nav>
    );
}
