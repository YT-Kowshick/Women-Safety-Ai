import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import SafetyCheck from "./pages/SafetyCheck";
import Simulation from "./pages/Simulation";
import CrimeTrends from "./pages/CrimeTrends";
import Heatmap from "./pages/Heatmap";
import Leaderboard from "./pages/Leaderboard";
import Recommendations from "./pages/Recommendations";
import SOSEmergency from "./pages/SOSEmergency";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/safety-check" element={<SafetyCheck />} />
          <Route path="/simulation" element={<Simulation />} />
          <Route path="/trends" element={<CrimeTrends />} />
          <Route path="/heatmap" element={<Heatmap />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/sos" element={<SOSEmergency />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
