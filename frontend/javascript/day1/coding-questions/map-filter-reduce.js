const arr=[5,1,3,2,6];

//double -[10,2,6,4,12]

//triple-[15,3,9,18]

//binary-["101","1","11","10","110"]


function double(x){
    return x * 2;
}

const output = arr.map(double);
console.log(output)
function triple(x){
    return x*3;
}
const output2 = arr.map(triple);
console.log(output2)


function binary(x){
    return x.toString(2);
}
const output3=arr.map(binary);
console.log(output3);

//filter function
function isOdd(x){
    return x%2;
}
const result=arr.filter(isOdd);
console.log(result);


function iseven(x){
    return x%2===0;
}
const result1=arr.filter(iseven);
console.log(result1)


