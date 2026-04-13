
import React,{Component} from 'react'
import Greet1 from './components/Greet1'
import Welcome1 from './components/Welcome1'
import Counter from './counter';

class App extends React.Component {
  render() {
    return (
      <div className="App">
        <Greet1 />
        <Welcome1 />
        <Counter />
      </div>
    );
  }
} 


export default App
