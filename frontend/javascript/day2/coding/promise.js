//creating promise
const myPromise =new Promise((resolve,reject)=>{
    const success=true;
    if (success){
        resolve("Here is your data");
    }else{
        reject("something went wrong");
    }
});


//consuming a promise -.then(),.catch(),.finally()
myPromise
    .then(result=>{
        console.log(result);
    })
    .catch(error=>{
        console.log(error);
    })
    .finally(()=>{
        console.log("always runs,success or fail");
    })