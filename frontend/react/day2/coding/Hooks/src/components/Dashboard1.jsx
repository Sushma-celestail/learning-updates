


function Dashboard1(){


    return (
        <p>What happens internally?
App loads → only main bundle is downloaded
Dashboard is NOT loaded yet
When React reaches 
It triggers a separate request (chunk file)
That component loads dynamically
Suspense fallback shows loading UI in meantime</p>
    );
}

export default Dashboard1;