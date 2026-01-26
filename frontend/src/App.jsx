import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ReportPage from "./pages/ReportPage";
import IEEEPage from "./pages/IEEEPage";
import SectionsPage from "./pages/SectionsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/report/:projectId" element={<ReportPage />} />
        <Route path="/ieee/:projectId" element={<IEEEPage />} />
        <Route path="/sections/:projectId" element={<SectionsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;