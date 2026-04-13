
import React  from 'react'

export default class Counter extends React.Component {
    constructor(props){
        super(props)
        this.state={
            counter:0
        }
        this.increment=()=>{this.setState({counter:this.state.counter+1})};
        this.decrement=()=>{this.setState({counter:this.state.counter-1})};
      
    }
    componentDidMount(){
        console.log('Component mounted');
        console.log('----------------')
    }
  
  render() {
    console.log('Rendering Counter');
    return (
    <div>
        <button onClick={this.increment}>Increment</button>
        <button onClick={this.decrement}>Decrement</button>
      <div className='counter'>
        Counter:{this.state.counter}
        </div>
    </div>
    )
  }
  componentDidUpdate(props,prevState,snapshot){
    console.log('Component updated');
    console.log('Previous State:', prevState);
    console.log('Current State:', this.state);
    console.log('----------------')
  }
}

