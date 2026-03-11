import "@/App.css";
import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { Toaster } from "@/components/ui/sonner";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ProblemsPage from "@/pages/ProblemsPage";
import ProblemSolvePage from "@/pages/ProblemSolvePage";
import DashboardPage from "@/pages/DashboardPage";
import CompilerPage from "@/pages/CompilerPage";
import CoachPage from "@/pages/CoachPage";
import MyPlanPage from "@/pages/MyPlanPage";
import PrivacyPage from "@/pages/PrivacyPage";
import TermsPage from "@/pages/TermsPage";

function App() {
  useEffect(() => {
    document.title = "If Else";
  }, []);
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/problems" element={<ProblemsPage />} />
          <Route path="/problems/:problemId" element={<ProblemSolvePage />} />
          <Route path="/compiler" element={<CompilerPage />} />
          <Route path="/coach" element={<CoachPage />} />
          <Route path="/my-plan" element={<MyPlanPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </AuthProvider>
  );
}

export default App;
