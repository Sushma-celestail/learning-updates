import {useContext} from "react";

import {ThemeContext, UserContext} from "../context";

function Dashboard(){
    const {theme, toggleTheme} =useContext(ThemeContext);
    const user=useContext(UserContext);


    return (
        <div style ={{
            background: theme === "dark" ? "#222" : "#fff",
            color:  theme === "dark" ? "#fff" :"#000",
            padding: "20px"
        }}>
            <h1>Welcome, {user.name}</h1>
            <button onClick={toggleTheme}>Toggle Theme  </button>
        </div>
    );
}

export default Dashboard;