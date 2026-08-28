import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import SinglePrediction from './pages/SinglePrediction';
import BatchPrediction from './pages/BatchPrediction';
import ModelPerformance from './pages/ModelPerformance';
import AdvanceCalculator from './pages/AdvanceCalculator';
import RiskDashboard from './pages/RiskDashboard';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/predict" element={<SinglePrediction />} />
          <Route path="/batch" element={<BatchPrediction />} />
          <Route path="/performance" element={<ModelPerformance />} />
          <Route path="/advance" element={<AdvanceCalculator />} />
          <Route path="/risk" element={<RiskDashboard />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
