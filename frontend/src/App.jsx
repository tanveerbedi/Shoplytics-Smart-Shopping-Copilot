import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import DashboardPage from "./pages/DashboardPage";
import Navbar from "./components/shared/Navbar";

export default function App() {
  return (
    <div className="flex flex-col min-h-screen relative font-sans">
      {/* Shared Navbar for all routes */}
      <Navbar />

      {/* Main Routing */}
      <main className="flex-1 flex flex-col h-full mt-14">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </main>
    </div>
  );
}
