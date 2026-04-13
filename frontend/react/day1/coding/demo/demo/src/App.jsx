import "./App.css";
import ProfileCard from "./components/ProfileCard";
// import React,{ useState } from "react";
import FunctionClick  from "./components/functionclick";
import LoginForm from "./components/LoginForm";


// function Header(){
//   return <h1>I am header</h1>
// }
// function Main(){
//   return <h3>Main content</h3>
// }
// function Greeting(props){
//   return <h4>Hello,{props.name}!</h4>
// }
// function Card({title,description}){
//   return(
//     <div class="card">
//       <h6>{title}</h6>
//       <p>{description}</p>
//     </div>
//   );
// }

// function Footer(){
//   return <h5>I am footer</h5>
// }
// function App(){
//   return(
//     <div>
//       <Header/>
//       <Main/>
//       <Greeting name="sushma"/>
//       <Card title="card1" description="Firast card"/>
//       <Card title="card2" description="second card"/>
//       <Card title="card3" description="third card"/>
//       <Footer/>
//     </div>
//   );
// }
function HandleClick(e) {
    e.preventDefault();    // Stops the BROWSER's default action (form submit, link nav...)
    e.stopPropagation();   // Stops the event BUBBLING UP to parent elements
}
function App(){
  // const [count,setCount]=useState(4);
  // function decrementCount(){
  //   setCount(previousCount => previousCount - 1)
  //   setCount( previousCount=> previousCount - 1)
  // }
  // function incrementCount(){
  //   setCount(previousCount=>previousCount+1)
  // }
  return (
  <div className="app">
    <FunctionClick/>
    <LoginForm/>
    <ProfileCard
      name="Sushma"
      title="Software Engineer"
      bio="Passionate abaout data and ai"
      avatarUrl="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTFnojo9Iy5hjW_KaaSn7tz9Amuyq-cetWpUrd3bRAxRJIKtN-Klv0QYI4&static/img/avatar/1.jpg"
    />
    <ProfileCard
        name="Anita"
        title="Data Scientist"
        bio="Works with AI and Deep Learning"
        avatarUrl="https://randomuser.me/api/portraits/women/3.jpg"
      />
  
    {/* <button onClick={decrementCount}>-</button>
    <span>{count}</span>
    <button onClick={incrementCount}>+</button>
     */}
    

 
  </div>
  
  
  );
}


export default App;