import React from 'react'
    const persons=[
        {
            id:1,
            name:'sushma',
            age:30,
            skill:'react'
        },
           {
            id:2,
            name:'Sahana',
            age:30,
            skill:'react'
        },
           {
            id:3,
            name:'Roopa',
            age:30,
            skill:'react'
        },
           {
            id:4,
            name:'Pranati',
            age:30,
            skill:'react'
        },
    ]
    function NameList() {
   return (
    <div>
        {persons.map((person)=>(
            <div key={person.id}>
                <h3>{person.name}</h3>
                <p>{person.age}</p>
                <p>{person.skill}</p>
            </div>
        ))}

    {persons.map((person)=>(
        <div key={person.id}>
            <h2>{person.name}</h2>
            <p>{person.age}</p>
            <ul>
                {person.skill.map((skill,index)=>(
                    <li key={index}>{skill}</li>
                ))}
            </ul>
        </div>

    ))}
</div>


);
}

export default NameList