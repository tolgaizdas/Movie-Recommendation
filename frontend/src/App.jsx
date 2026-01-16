import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Recommendations from './pages/Recommendations';
import MyList from './pages/MyList';
import PrivateRoute from './components/PrivateRoute'; // We need this

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/recommendations" element={
            <PrivateRoute>
              <Recommendations />
            </PrivateRoute>
          } />
          <Route path="/mylist" element={
            <PrivateRoute>
              <MyList />
            </PrivateRoute>
          } />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
