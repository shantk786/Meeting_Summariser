import Navbar from './components/Navbar';
import Home from './pages/Home';

function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main>
        <Home />
      </main>
    </div>
  );
}

export default App;
