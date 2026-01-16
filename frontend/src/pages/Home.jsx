import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';

const API_URL = import.meta.env.VITE_API_URL;

export default function Home() {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchMovies() {
            try {
                const response = await axios.get(`${API_URL}/movies/`);
                setMovies(response.data);
            } catch (error) {
                console.error("Error fetching movies:", error);
            }
            setLoading(false);
        }

        fetchMovies();
    }, []);

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            <Navbar />
            <div className="container mx-auto p-8">
                <h1 className="text-3xl font-bold mb-6">Popular Movies</h1>
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {movies.map((movie) => (
                            <div key={movie.movie_id} className="bg-gray-800 rounded-lg overflow-hidden shadow-lg hover:shadow-2xl transition duration-300">
                                <div className="p-6">
                                    <h2 className="text-xl font-bold mb-2">{movie.title}</h2>
                                    <p className="text-gray-400 text-sm mb-4">{movie.genres.join(", ")} • {movie.year}</p>
                                    <div className="flex items-center justify-between">
                                        <span className="bg-yellow-600 text-xs font-bold px-2 py-1 rounded text-black">
                                            ★ {movie.average_rating}
                                        </span>
                                        <button className="text-red-500 hover:text-red-400 font-semibold text-sm">
                                            Rate This
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
