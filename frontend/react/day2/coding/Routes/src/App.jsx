
import {BrowserRouter,Routes,Route,NavLink} from "react-router-dom";
import Home from './assets/components/Home';
import About from './assets/components/About';
import Contact from './assets/components/Contact';
import NotFound from './assets/components/NotFound';
function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: "20px" }}>
        <NavLink to="/" end style={({ isActive }) => ({
          color: isActive ? "red" : "black"
        })}>
          Home
        </NavLink>

<NavLink to="/about" style={({ isActive})=>({
  color : isActive ? "red":"black"
})}>About</NavLink>

<NavLink to="/contact" style={({isActive})=>({
  color:isActive ? "red" : "black"
})}>Conatct</NavLink>





    </nav>
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/about" element={<About/>}/>
      <Route path="/contact" element={<Contact/>}/>
      <Route path="*" element={<NotFound/>}/>
    </Routes>
      </BrowserRouter>)
}

export default App