// import React,{useState} from 'react'

// function First() {
//   const[formData,setFormData]=useState({
//     name:"",
//   });

//   const handleChange=(e)=>{
//     const {name,value}=e.target;
//     setFormData({
//       ...formData,
//       [name]:value
//     });
//   };

//   const handleSubmit=(e)=>{
//     e.preventDefault();
//     console.log("form data",formData);
//     alert("form submitted successfully");
//   };


//  return (
//     <div>
//    <form onSubmit={handleSubmit}>
//     <h2>Register here</h2>
//     <input type='text'
//       name='name'
//       placeholder='enter name'
//       value={formData.name}
//       onChange={handleChange}
//       required
//       />
//   <button type='submit'>Submit</button>
  
//    </form>
//     </div>
    
//   )
// }

// export default First;



import React,{useState} from 'react';
function First(){

const [formData, setFormData]=useState({
  name:""
})

const handleChange=(e)=>{
  const {name,value}=e.target;
  setFormData({
    ...formData,
    [name]:value
  });
}
const handleSubmit=(e)=>{
  e.preventDefault();
  console.log(formData);
  alert("form submitted successfully");
}
 const handleClick = () => {
    alert("Button clicked!");
    console.log(formData);
  };

return (
  <div>
    <form onSubmit={handleSubmit}>
      <h1>Registration form</h1>
      <input 
        type='text'
        name='name'
        placeholder='enter name'
        value={formData.name}
        onChange={handleChange}
        required
        />
        <button type='submit' onClick={handleClick}>Submit</button>
    </form>
  </div>

)
}
export default First;