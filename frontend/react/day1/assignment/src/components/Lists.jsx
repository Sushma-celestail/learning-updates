import React from 'react'
import './lists.css'

function Lists(props) {
    let className=props.primary?'primary':'secondary'

  return (
    <div>
        <h1 className={`${className} font-xl`}>Lists in react</h1>
    </div>
  )
}

export default Lists