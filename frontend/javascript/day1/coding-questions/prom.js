// cart=["shoes","shirts","pants"];

// // createOrder(cart,function(orderId){
// //     proceedToPayment(orderId,function paymentInfo(paymentDetails){
// //     showOrderSummary(paymentDetails);
// //     });
// // });


// createOrder(cart,function(orderId){
//     proceedToPayment(orderId);
// });
// const promise=createOrder(cart);

// Funtion to display something
function myDisplayer(some) {
  document.getElementById("demo").innerHTML = some;
}

// Create a Promise Object
let myPromise = new Promise(function(resolve, reject) {
  ok = true;

// Code that might take some time goes here

  if (ok) {
    resolve("OK");
  } else {
    reject("Error");
  }
});

// Using then() to display the result
myPromise.then(
  function(value) {myDisplayer(value)},
  function(value) {myDisplayer(value)}
);
