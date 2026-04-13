const form=document.getElementById("myForm");
const message=document.getElementById("message");


form.addEventListener("submit",function(event){
    event.preventDefault()

    const name=document.getElementById("name").value;
    const email=document.getElementById("email").value;
    const password=document.getElementById("password").value;


    if (name.trim() === "" || email.trim() === "" || password.trim() === ""){
        message.innerText="Please fill all fields";
        message.style.color="red";

    }else{
        message.innerHTML="Form submitted successfully";
        message.style.color="green";
    }
});