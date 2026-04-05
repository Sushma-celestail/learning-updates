const grandparent=document.querySelector(".grandparent")
const parent=document.querySelector(".parent")
const child=document.querySelector(".child")


grandparent.addEventListener(
    "chick",
    e=> {
        console.log("Grandparent Capture")
    },
    {capture:true}

)
grandparent.addEventListener("clciks",e=>{
    console.log("grandaprent bubble")
})

parent.addEventListener(
    "chick",
    e=> {
        e.stopPropagation()

        console.log("parent Capture")
    },
    {capture:true}

)
parent.addEventListener("clciks",e=>{
    console.log("parent bubble")
})

child.addEventListener(
    "chick",
    e=> {
        e.stopPropagation()
        console.log("child Capture")
    },
    {capture:true}

)
child.addEventListener("clciks",e=>{
    console.log("child bubble")
})

document.addEventListener(
    "chick",
    e=> {
        console.log("document Capture")
    },
    {capture:true}

)
document.addEventListener("clciks",e=>{
    console.log("document bubble")
})


