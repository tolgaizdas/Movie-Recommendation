import React, { useRef, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
    const emailRef = useRef();
    const passwordRef = useRef();
    const { login } = useAuth();
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    async function handleSubmit(e) {
        e.preventDefault();

        try {
            setError('');
            setLoading(true);
            await login(emailRef.current.value, passwordRef.current.value);
            navigate('/');
        } catch (e) {
            console.error(e);
            setError('Failed to sign in. (For prototype: check console/config)');
        }

        setLoading(false);
    }

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-900">
            <div className="bg-gray-800 p-8 rounded shadow-lg max-w-md w-full">
                <h2 className="text-2xl font-bold mb-6 text-white text-center">Login</h2>
                {error && <div className="bg-red-500 text-white p-3 mb-4 rounded">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-gray-400 mb-2">Email</label>
                        <input
                            type="email"
                            ref={emailRef}
                            required
                            className="w-full p-2 rounded bg-gray-700 text-white border border-gray-600 focus:outline-none focus:border-red-500"
                        />
                    </div>
                    <div className="mb-6">
                        <label className="block text-gray-400 mb-2">Password</label>
                        <input
                            type="password"
                            ref={passwordRef}
                            required
                            className="w-full p-2 rounded bg-gray-700 text-white border border-gray-600 focus:outline-none focus:border-red-500"
                        />
                    </div>
                    <button
                        disabled={loading}
                        className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition duration-200"
                        type="submit"
                    >
                        Log In
                    </button>
                </form>
                <div className="mt-4 text-center text-sm text-gray-400">
                    Need an account? <Link to="/signup" className="text-red-500 hover:text-red-400">Sign Up</Link>
                </div>
            </div>
        </div>
    );
}
