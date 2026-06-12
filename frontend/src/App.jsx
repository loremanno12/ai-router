
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import AIRouter from "./features/AIRouter"; // Percorso aggiornato
import PageNotFound from "./components/PageNotFound";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AIRouter />} />
        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </Router>
  );
}
