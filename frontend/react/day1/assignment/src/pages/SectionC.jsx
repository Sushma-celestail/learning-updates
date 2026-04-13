import { useState, useEffect } from "react";

const SectionC = () => {
  const [time, setTime] = useState(new Date());
  const [running, setRunning] = useState(true);
  const [users, setUsers] = useState([]);
  const [count, setCount] = useState(0);

  // Clock
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, [running]);

  // Fetch users
  const fetchUsers = async () => {
    const res = await fetch("https://jsonplaceholder.typicode.com/users");
    const data = await res.json();
    setUsers(data);
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Title
  useEffect(() => {
    document.title = `Count: ${count}`;
    return () => (document.title = "React App");
  }, [count]);

  return (
    <div>
      <h2>Section C</h2>

      {/* Q9 */}
      <h3>{time.toLocaleTimeString()}</h3>
      <button onClick={() => setRunning(!running)}>
        {running ? "Pause" : "Resume"}
      </button>

      {/* Q10 */}
      <button onClick={fetchUsers}>Refresh</button>
      {users.map(u => <p key={u.id}>{u.name}</p>)}

      {/* Q11 */}
      <button onClick={() => setCount(count + 1)}>+</button>
      <button onClick={() => setCount(count - 1)}>-</button>
    </div>
  );
};

export default SectionC;