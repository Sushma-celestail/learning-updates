
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


// import React, { Suspense, useState } from "react";
// import Dashboard1 from "./components/Dashboard1";
// const Dashboard = React.lazy(() => import("./components/Dashboard"));

// function App() {
//   const [showDashboard, setShowDashboard] = useState(false);

//   return (
//     <div>
//       <h1>My App</h1>

//       {/* Show Dashboard1 initially */}
//       {!showDashboard && (
//         <>
//           <Dashboard1 />
//           <button onClick={() => setShowDashboard(true)}>
//             Go to Dashboard
//           </button>
//         </>
//       )}

//       {/* Load Dashboard only on click */}
//       {showDashboard && (
//         <Suspense fallback={<p>Loading...</p>}>
//           <Dashboard />
//         </Suspense>
//       )}
//     </div>
//   );
// }

// export default App;


// import React, { Suspense } from "react";

// const HeavyComponent = React.lazy(() => import("./components/HeavyComponent"));

// function App() {
//   return (
//     <div>
//       <h1>My App</h1>

//       <Suspense fallback={<div className="spinner">🔄 Loading...</div>}>
//         <HeavyComponent />
//       </Suspense>

  
//     </div>
//   );
// }

// export default App;

import React,{useEffect} from "react";
import { useSelector,useDispatch } from "react-redux";
import { increment, decrement, incrementByAmount, reset } from "./slices/counterSlice";
import { fetchUsers } from "./slices/userSlice";

function App(){
  const count=useSelector((state)=>state.counter.value);
   const users = useSelector((state) => state.user.users);
  const status = useSelector((state) => state.user.status);
  const dispatch=useDispatch();
  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);
  return (
   <div style={{ textAlign: "center" }}>
      <h1>Redux Toolkit Demo</h1>

      {/* Counter */}
      <h2>Count: {count}</h2>
      <button onClick={() => dispatch(increment())}>+</button>
      <button onClick={() => dispatch(decrement())}>-</button>
      <button onClick={() => dispatch(incrementByAmount(5))}>+5</button>
      <button onClick={() => dispatch(reset())}>Reset</button>

      {/* Users */}
      <h2>Users</h2>
      {status === "loading" && <p>Loading...</p>}
      {users.map(user => (
        <p key={user.id}>{user.name}</p>
      ))}
    </div>
  );
}

export default App;