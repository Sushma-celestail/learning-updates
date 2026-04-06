//axios globals
axios.defaults.headers.common['X-Auth-Token']='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30';


// GET REQUEST
function getTodos() {
//   axios({
//     method:'get',
//     url:'https://jsonplaceholder.typicode.com/todos',
//     params:{
//         _limit:5
//   }
//   })
//   .then(res => showOutput(res))
//   .catch(err=>console.log(err))
axios('https://jsonplaceholder.typicode.com/todos?_limit=5')
    .then(res => showOutput(res))
    .catch(err=> console.error(err))
}

// POST REQUEST
function addTodo() {
//     axios({
//     method:'post',
//     url:'https://jsonplaceholder.typicode.com/todos',
//     data:{
//         title:'New Todo',
//         completed:false
//   }
//   })
//   .then(res => showOutput(res))
//   .catch(err=>console.log(err))
axios.post('https://jsonplaceholder.typicode.com/todos',{
    
    title:'new todo',
    completed:false
})
    .then(res => showOutput(res))
    .catch(err=>console.log(err))
}

// PUT/PATCH REQUEST
function updateTodo() {
  axios.put('https://jsonplaceholder.typicode.com/todos/1',{
    title:'Updated todo',
    completed:false
})
    .then(res=> showOutput(res))
    .catch(err=>console.error(err)) 
}


function updateTodo() {
  axios.patch('https://jsonplaceholder.typicode.com/todos/1',{
    title:'Updated todo',
    completed:false
})
    .then(res=> showOutput(res))
    .catch(err=>console.error(err)) 
}


// DELETE REQUEST
function removeTodo() {
  axios
    .delete('https://jsonplaceholder.typicode.com/todos/1')
    .then(res=> showOutput(res))
    .catch(err=>console.error(err)) 
}


// SIMULTANEOUS DATA
function getData() {
  axios.all([
    axios.get('https://jsonplaceholder.typicode.com/todos?_limit=5'),
    axios.get('https://jsonplaceholder.typicode.com/posts?_limit=5')
  ])
  .then(axios.spread((todos,posts)=> showOutput(posts)))
  .catch(err=>console.error(err));
}

// CUSTOM HEADERS
function customHeaders() {
  console.log('Custom Headers');
}

// TRANSFORMING REQUESTS & RESPONSES
function transformResponse() {
  console.log('Transform Response');
}

// ERROR HANDLING
function errorHandling() {
  axios
    .delete('https://jsonplaceholder.typicode.com/todoss')
    .then(res=> showOutput(res))
    .catch(err=>{
        console.log(err.response.data);
        console.log(err.response.status);
        console.log(err.response.header);
        if(err.response.status===404){
            alert('Errorpage not found')
        }
    }

    ) 
}


// CANCEL TOKEN
function cancelToken() {
  console.log('Cancel Token');
}

// INTERCEPTING REQUESTS & RESPONSES





// AXIOS INSTANCES







// Show output in browser
function showOutput(res) {
  document.getElementById('res').innerHTML = `
  <div class="card card-body mb-4">
    <h5>Status: ${res.status}</h5>
  </div>

  <div class="card mt-3">
    <div class="card-header">
      Headers
    </div>
    <div class="card-body">
      <pre>${JSON.stringify(res.headers, null, 2)}</pre>
    </div>
  </div>

  <div class="card mt-3">
    <div class="card-header">
      Data
    </div>
    <div class="card-body">
      <pre>${JSON.stringify(res.data, null, 2)}</pre>
    </div>
  </div>

  <div class="card mt-3">
    <div class="card-header">
      Config
    </div>
    <div class="card-body">
      <pre>${JSON.stringify(res.config, null, 2)}</pre>
    </div>
  </div>
`;
}

// Event listeners
document.getElementById('get').addEventListener('click', getTodos);
document.getElementById('post').addEventListener('click', addTodo);
document.getElementById('update').addEventListener('click', updateTodo);
document.getElementById('delete').addEventListener('click', removeTodo);
document.getElementById('sim').addEventListener('click', getData);
document.getElementById('headers').addEventListener('click', customHeaders);
document
  .getElementById('transform')
  .addEventListener('click', transformResponse);
document.getElementById('error').addEventListener('click', errorHandling);
document.getElementById('cancel').addEventListener('click', cancelToken);