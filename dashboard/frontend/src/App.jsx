import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ControlCenter from './pages/ControlCenter';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/control-center" element={<ControlCenter />} />
      </Routes>
    </Router>
  );
}

export default App;
