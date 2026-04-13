import React from 'react'

function Child(props) {
    const greet="good afternoon";
  return (
    <div> Hello Child good morning 

    <button 
    onClick={()=>{
        props.func(greet);
    }}>
        Update
    </button>
    </div>
  )
}

export default Child