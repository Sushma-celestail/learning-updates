import { useState } from "react";

const SectionB = () => {
  const [count, setCount] = useState(0);
  const [dark, setDark] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [task, setTask] = useState("");
  const [tasks, setTasks] = useState([]);

  const students = [
    { name: "A", marks: 80 },
    { name: "B", marks: 30 },
    { name: "C", marks: 60 }
  ];

  return (
    <div style={{ background: dark ? "#000" : "#fff", color: dark ? "#fff" : "#000" }}>
      <h2>Section B</h2>

      {/* Q4 Counter */}
      <p>{count}</p>
      <button disabled={count <= 0} onClick={() => setCount(count - 1)}>-</button>
      <button disabled={count >= 10} onClick={() => setCount(count + 1)}>+</button>
      <button onClick={() => setCount(0)}>Reset</button>

      {/* Q5 Theme */}
      <button onClick={() => setDark(!dark)}>Toggle Theme</button>

      {/* Q6 Login */}
      <button onClick={() => setLoggedIn(!loggedIn)}>
        {loggedIn ? "Logout" : "Login"}
      </button>
      <p>{loggedIn ? "Welcome User!" : "Please login"}</p>

      {/* Q7 Todo */}
      <input value={task} onChange={e => setTask(e.target.value)} />
      <button onClick={() => setTasks([...tasks, task])}>Add</button>
      {tasks.length === 0 ? <p>No tasks</p> : tasks.map((t, i) => <p key={i}>{t}</p>)}

      {/* Q8 Students */}
      {students.map((s, i) => (
        <p key={i} style={{ color: s.marks > 75 ? "green" : s.marks < 35 ? "red" : "black" }}>
          {s.name} - {s.marks}
        </p>
      ))}
    </div>
  );
};

export default SectionB;