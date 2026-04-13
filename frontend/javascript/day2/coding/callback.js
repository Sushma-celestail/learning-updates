function sayHello(){
    console.log("hello");
}setTimeout(sayHello,5000);

//callback with data
function getUser(id,callback){
    setTimeout(()=>{
        const user={id:id,name:"sushma"};
        callback(user);
    },1000);
}


getUser(1,function(user){
    console.log("got user:",user.name);
});
