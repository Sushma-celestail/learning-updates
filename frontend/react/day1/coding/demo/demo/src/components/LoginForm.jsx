import React from 'react'
import {useState} from "react";

function LoginForm() {
    const [formData,setFormData]=useState({
        email:"",
        password:""

    });
    const [message,setMessage]=useState("");
    function handleChange(e){
        setFormData({
            ...formData,
            [e.target.name]:e.target.value
        });
    }
        function handleSubmit(e){
            e.preventDefault();
            e.stopPropogation();

            console.log("Form Submitted",formData);

            if(formData.email==="admin@gmail.com" && formData.password==="1234"){
                setMessage("Login successful");
            }else{
                setMessage("Invalid credentials");
            }

        }
    
  return (
    <div onClick={()=>
        console.log("parent div clicked")}
    >
    <form onSubmit={handleSubmit}>
        <h2>Login Form</h2>
        <input
            type="email"
            name="email"
            placeholder='enter email'
            value={formData.email}
            onChange={handleChange}
        />
        <br></br>
        <input
            type="password"
            name="password"
            placeholder='enter password'
            value={formData.password}
            onChange={handleChange}
        />
        <br></br>

        <button type="submit">Login</button>
        </form>
        <p>{message}</p>

    </div>
  )
}

export default LoginForm