import React from 'react'
import First from './components/first';
function App() {
  const fruits=['Apple','Banana','Mango',"banan"];
  const element=<h1>welcome to the React</h1>;
  return (
    <div>
      {element}

      <h2>Home page</h2>
      <div>
        <First/>
      </div>
      <div>
        <ul>
          {fruits.map((item,index)=>(
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>

      
    </div>
    
  )
}

export default App