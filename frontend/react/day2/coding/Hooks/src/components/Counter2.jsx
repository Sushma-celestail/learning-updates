import React ,{useReducer} from 'react'

const initialState = {
    firstCounter: 0
}
const reducer =(state, action)=>{
    switch(action.type){
        case 'increment':
            return { ...state, firstCounter: state.firstCounter + action.value }
        case 'decrement':
            return { ...state, firstCounter: state.firstCounter - action.value }
        case 'reset':
            return initialState
        default:
            return state
    }
};
function Counter2() {

    const [count,dispatch] = useReducer(reducer,initialState);
    return (
    <div>
        <div> Count {count.firstCounter}</div> 
        <button onClick={()=> dispatch({type: 'increment',value:1})}>Increment</button>
        <button onClick={()=>dispatch({type: 'decrement',value:1})}>decrement</button>
        <button onClick={()=> dispatch({type: 'increment',value:5})}>Increment</button>
        <button onClick={()=>dispatch({type: 'decrement',value:5})}>decrement</button>
        <button onClick={()=>dispatch({type: 'reset'})}>Reset</button>
    </div>
  )
}

export default Counter2;