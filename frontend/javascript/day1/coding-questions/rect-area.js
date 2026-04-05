//function declarations

function rectangleArea(length,width){
    return length * width;
}
console.log(rectangleArea(5,3));

//function expression
const rectangleAreaExpr=function(length,width){
    return length * width;
};
console.log(rectangleAreaExpr(5,3));


//arrow function
const rectangleAreaExprArrow=(length,width) =>length* width;
console.log(rectangleAreaExprArrow(5,3));