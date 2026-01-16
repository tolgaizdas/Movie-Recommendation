import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import { useAuth } from '../contexts/AuthContext';

const API_URL = import.meta.env.VITE_API_URL;

export default function MyList() {
    const [searchQuery, setSearchQuery] = useState('');
    const [movies, setMovies] = useState([]);
    const [ratedMovies, setRatedMovies] = useState({}); // Map movie_id -> rating
    const [myListDetails, setMyListDetails] = useState([]); // Array of movie objects with ratings
    const [loading, setLoading] = useState(false);
    const { currentUser } = useAuth();

    // Fetch user's existing ratings on load
    useEffect(() => {
        async function fetchMyRatings() {
            if (!currentUser) return;
            try {
                const token = await currentUser.getIdToken();
                const response = await axios.get(`${API_URL}/ratings/`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const ratingsMap = {};
                // Backend now returns array of { ...movie, my_rating: X }
                response.data.forEach(r => {
                    ratingsMap[r.movie_id] = r.my_rating || r.rating; // handle both formats just in case
                });
                setRatedMovies(ratingsMap);
                setMyListDetails(response.data);
            } catch (error) {
                console.error("Error fetching my ratings:", error);
            }
        }
        fetchMyRatings();
    }, [currentUser]);

    async function handleSearch(e) {
        e.preventDefault();
        setLoading(true);
        try {
            // Note: Token not strictly required for public GET /movies but good practice if we lock it down
            const response = await axios.get(`${API_URL}/movies/`, {
                params: { search: searchQuery }
            });
            setMovies(response.data);
        } catch (error) {
            console.error("Error searching movies:", error);
        }
        setLoading(false);
    }

    async function handleRate(movieId, rating) {
        try {
            const token = await currentUser.getIdToken();
            await axios.post(`${API_URL}/ratings/`, {
                movie_id: movieId,
                rating: rating
            }, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            // Update local state
            setRatedMovies(prev => ({
                ...prev,
                [movieId]: rating
            }));

            // Also update the list details if it's there
            setMyListDetails(prev => {
                const existing = prev.find(m => m.movie_id === movieId);
                if (existing) {
                    return prev.map(m => m.movie_id === movieId ? { ...m, my_rating: rating } : m);
                }
                // If not in list (searched new movie), we should strictly refresh list or add it manually.
                // For prototype simplicity, let's just re-fetch the list details silently or wait for refresh.
                // Or better, manually construct it if we have the movie in 'movies' state.
                const searchedMovie = movies.find(m => m.movie_id === movieId);
                if (searchedMovie) {
                    return [...prev, { ...searchedMovie, my_rating: rating }];
                }
                return prev;
            });

        } catch (error) {
            console.error("Error saving rating:", error);
            alert("Failed to save rating");
        }
    }

    async function handleDelete(movieId) {
        if (!confirm("Remove this movie from your ratings?")) return;
        try {
            const token = await currentUser.getIdToken();
            await axios.delete(`${API_URL}/ratings/${movieId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            // Remove from local state
            setRatedMovies(prev => {
                const next = { ...prev };
                delete next[movieId];
                return next;
            });
            setMyListDetails(prev => prev.filter(m => m.movie_id !== movieId));

        } catch (error) {
            console.error("Error deleting rating:", error);
        }
    }



    return (
        <div className="min-h-screen bg-gray-900 text-white">
            <Navbar />
            <div className="container mx-auto p-8">
                <h1 className="text-3xl font-bold mb-6">My Watchlist & Ratings</h1>

                {/* Search Section */}
                <form onSubmit={handleSearch} className="mb-8 flex gap-4">
                    <input
                        type="text"
                        placeholder="Search for movies (e.g. 'Toy Story')..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="flex-1 p-3 rounded bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-red-500"
                    />
                    <button
                        type="submit"
                        className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded font-bold transition duration-200"
                    >
                        Search
                    </button>
                </form>

                {/* Results Section */}
                {loading ? (
                    <p className="text-gray-400">Searching...</p>
                ) : (
                    <div className="space-y-12">
                        {/* Search Results */}
                        {movies.length > 0 && (
                            <section>
                                <h2 className="text-2xl font-bold mb-4 border-b border-gray-700 pb-2">Search Results</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {movies.map((movie) => (
                                        <MovieCard
                                            key={movie.movie_id}
                                            movie={movie}
                                            rating={ratedMovies[movie.movie_id]}
                                            onRate={handleRate}
                                            onDelete={handleDelete}
                                        />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* My Rated List */}
                        <section>
                            <h2 className="text-2xl font-bold mb-4 border-b border-gray-700 pb-2">My Rated Movies</h2>
                            {Object.keys(ratedMovies).length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {myListDetails.map((movie) => (
                                        <MovieCard
                                            key={movie.movie_id}
                                            movie={movie}
                                            rating={movie.my_rating || ratedMovies[movie.movie_id]}
                                            onRate={handleRate}
                                            onDelete={handleDelete}
                                        />
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500">You haven't rated any movies yet.</p>
                            )}
                        </section>
                    </div>
                )}
            </div>
        </div>
    );
}

function MovieCard({ movie, rating, onRate, onDelete }) {
    return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 shadow-lg relative group">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h2 className="text-xl font-bold text-white mb-1">{movie.title}</h2>
                    <p className="text-sm text-gray-400">{Array.isArray(movie.genres) ? movie.genres.join(", ") : movie.genres}</p>
                </div>
                {movie.year > 0 && (
                    <span className="bg-gray-700 text-xs px-2 py-1 rounded text-gray-300">
                        {movie.year}
                    </span>
                )}
            </div>

            <div className="mt-4 border-t border-gray-700 pt-4 flex justify-between items-center">
                <div>
                    <p className="text-sm text-gray-400 mb-1">Your Rating:</p>
                    <div className="flex space-x-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                            <button
                                key={star}
                                onClick={() => onRate(movie.movie_id, star)}
                                className={`text-2xl focus:outline-none transition-colors duration-200 ${star <= (rating || 0) ? 'text-yellow-400' : 'text-gray-600 hover:text-yellow-200'
                                    }`}
                            >
                                ★
                            </button>
                        ))}
                    </div>
                </div>

                {rating > 0 && (
                    <button
                        onClick={() => onDelete(movie.movie_id)}
                        className="text-sm text-red-500 hover:text-red-400 underline mt-6"
                    >
                        Remove
                    </button>
                )}
            </div>
        </div>
    );
}
