import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import './App.css';

// Components
import Header from './components/Header';
import Footer from './components/Footer';

// Pages
import Home from './pages/Home';
import NearbyCenters from './pages/NearbyCenters';
import TestAnalysis from './pages/TestAnalysis';
import FoodProducts from './pages/FoodProducts';
import Medicines from './pages/Medicines';
import TestPrices from './pages/TestPrices';
import HospitalRouting from './pages/HospitalRouting';

function App() {
  return (
    <div className="App d-flex flex-column min-vh-100">
      <Header />
      <Container fluid className="flex-grow-1 py-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/nearby-centers" element={<NearbyCenters />} />
          <Route path="/test-analysis" element={<TestAnalysis />} />
          <Route path="/food-products" element={<FoodProducts />} />
          <Route path="/medicines" element={<Medicines />} />
          <Route path="/test-prices" element={<TestPrices />} />
          <Route path="/hospital-routing" element={<HospitalRouting />} />
        </Routes>
      </Container>
      <Footer />
    </div>
  );
}

export default App;
