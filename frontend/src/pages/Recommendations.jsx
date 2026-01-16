import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL;

export default function Recommendations() {
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);
    const { currentUser } = useAuth();

    useEffect(() => {
        async function fetchRecommendations() {
            if (!currentUser) return;
            try {
                const response = await axios.post(`${API_URL}/recommendations/`, {
                    user_id: currentUser.uid || "test_user",
                    num_recommendations: 6
                });
                setRecommendations(response.data);
            } catch (error) {
                console.error("Error fetching recommendations:", error);
            }
            setLoading(false);
        }

        fetchRecommendations();
    }, [currentUser]);

    if (!currentUser) {
        return (
            <div className="min-h-screen bg-gray-900 text-white">
                <Navbar />
                <div className="container mx-auto p-8 text-center">
                    <p>Please log in to see recommendations.</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            <Navbar />
            <div className="container mx-auto p-8">
                <h1 className="text-3xl font-bold mb-2">Recommended for You</h1>
                <p className="text-gray-400 mb-6">Based on your viewing history</p>

                {loading ? (
                    <p>Personalizing your list...</p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {recommendations.map((movie) => (
                            <div key={movie.movie_id} className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden shadow-lg hover:scale-105 transition transform duration-300">
                                <div className="p-6">
                                    <h2 className="text-xl font-bold mb-2 text-red-500">{movie.title}</h2>
                                    <p className="text-gray-400 text-sm mb-4">{movie.genres.join(", ")}</p>
                                    <span className="block bg-gray-900 text-center py-2 rounded text-sm text-gray-300">
                                        Match Score: {Math.floor(movie.average_rating * 20)}%
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
