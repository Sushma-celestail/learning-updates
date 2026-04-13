
//using axios with promises
// const btn = document.getElementById("btn");
// const list = document.getElementById("list");
// const status = document.getElementById("status");

// btn.addEventListener("click", function () {
//   status.innerHTML = "Loading...";
//   list.innerHTML = "";

//   axios.get("https://jsonplaceholder.typicode.com/users")
//     .then(function (response) {
//       status.innerHTML = "";

//       response.data.forEach(user => {
//         list.innerHTML += `<li>${user.name}</li>`;
//       });
//     })
//     .catch(function (error) {
//       status.innerHTML = "Error fetching data";
//     });
// });







//using Async/Await
const btn = document.getElementById("btn");
const list = document.getElementById("list");
const status = document.getElementById("status");

btn.addEventListener("click", getUsers);

async function getUsers() {
  status.innerHTML = "Loading...";
  list.innerHTML = "";

  try {
    const response = await axios.get("https://jsonplaceholder.typicode.com/users");

    status.innerHTML = "";

    response.data.forEach(user => {
      list.innerHTML += `<li>${user.name}</li>`;
    });

  } catch (error) {
    status.innerHTML = "Error fetching data";
  }
}