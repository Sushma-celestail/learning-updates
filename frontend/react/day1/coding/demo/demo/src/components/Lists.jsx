import React from 'react'

function Lists() {
    const fruits=["apple","banana","orange"];
    const users=[
        {id:1,name:"sushma",role:"admin"},
        {id:2,name:"suma",role:"editor"},
        {id:3,name:"sush",role:"viewer"}

    ]
  return (
<div>
 <ul>
    {fruits.map(fruits =>(
        <li key={fruits}>{fruits}</li>
    ))}
 </ul>
<ul>
            {users.map(user => (
                <li key={user.id}>
                    <strong>{user.name}</strong> — {user.role}
                </li>
            ))}
        </ul>
</div>
  );

}


export default Lists