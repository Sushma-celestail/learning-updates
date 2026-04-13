
// import React from "react"
// //import LoginForm from "./components/LoginForm"
// import Child from "./components/Child"

// function App() {
  
//   function parent(greet){
//     alert(greet)
//   }
//   return (
//   <>
//   <Child func={parent}/>
//   </>
//   )
// }

// export default App



import Dashboard from "./components/Dashboard";
import {ThemeProvider,UserProvider} from "./context";

function App(){
  return (
    
    <ThemeProvider>
      <UserProvider>
        <Dashboard/>
      </UserProvider>
    </ThemeProvider>
  )
}

export default App;