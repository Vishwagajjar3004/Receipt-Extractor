import Home from "./pages/Home.jsx";

/**
 * App
 * ---
 * Root component. Currently a single-page app, so it simply renders
 * the Home page. Kept separate from Home.jsx so routing could be added
 * later (e.g. react-router) without restructuring the page components.
 */
export default function App() {
  return <Home />;
}
