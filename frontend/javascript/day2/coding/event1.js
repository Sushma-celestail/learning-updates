var child =document.querySelector('#child'),
    mouseOver,
    mouseEnter,
    mouseLeave;

// Selects the first element with class="child"
// child
//  Stores that element so we can use it later
// mouseOver, mouseEnter, mouseLeave
//  Declares 3 variables (will hold functions later)

mouseOver=function mouseOver(){
    console.log("mouse over");
} 
mouseEnter=function mouseEnter(){
    console.log("mouse enter");
    child.style.cursor='wait';
}
mouseLeave=function mouseLeave(){
    console.log("mouse left");
    child.style.cursor='pointer';
}


child.addEventListener('mouseover',mouseOver);
child.addEventListener('mouseenter',mouseEnter);
child.addEventListener('mouseleave',mouseLeave);