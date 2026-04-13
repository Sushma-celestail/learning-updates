import React ,{useReducer} from 'react'

const initialState = 0
const reducer =(state, action)=>{
    switch(action.type){
        case 'increment':
            return state +1
        case 'decrement':
            return state-1 
        case 'reset':
            return initialState
        default:
            return state
    }
};
function Counter3() {

    const [count,dispatch] = useReducer(reducer,initialState);
    const [countTwo,dispatchTwo] = useReducer(reducer,initialState);
    return (
    <div>
        <div> Count {count}</div> 
        <button onClick={()=> dispatch({type: 'increment'})}>Increment</button>
        <button onClick={()=>dispatch({type: 'decrement'})}>decrement</button>
        <button onClick={()=>dispatch({type: 'reset'})}>Reset</button>
    
       <div>
        <div> Count {countTwo}</div> 
        <button onClick={()=> dispatchTwo({type: 'increment'})}>Increment</button>
        <button onClick={()=>dispatchTwo({type: 'decrement'})}>decrement</button>
        <button onClick={()=>dispatchTwo({type: 'reset'})}>Reset</button>
    </div>
    </div>
  )
}

export default Counter3;