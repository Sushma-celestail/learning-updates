document.querySelector("#grandparent")
    .addEventListener('click',(e)=> {
        console.log("grand parent clicked!");
            e.stopPropagation();
    },true); //capturing
    document.querySelector("#parent")
    .addEventListener('click',(e)=> {
        console.log("parent clicked!");
        e.stopPropagation();
    },true);//capturing
    document.querySelector("#child")
    .addEventListener('click',(e)=> {
        console.log("child clicked!");
        e.stopPropagation
    },true);//capturing
    