import React from 'react'

function Profile() {
    // const [formData,setForm]=useState(e);

    // const handlClick=(e)=>{
    //     e.defaul
    //     console.log("Application processed successfully",formData);  
    // }

  return (
    <div className='container'>
        <div>
            <h2>Profile </h2>
            <div>
                <label>Current job : Software engineer</label>
            </div>
            <div>
                <label>Company name : Celestials system private limited</label>
            </div>
            <div>
            <label>Start date : 9 March 2026</label>
            </div>
            <div>
            <label>Domain : Data & AI</label>
            </div>

        </div>
    </div>
  )
}

export default Profile