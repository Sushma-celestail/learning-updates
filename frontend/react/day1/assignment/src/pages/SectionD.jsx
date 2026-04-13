import { useState, useMemo, useCallback } from "react";
import TodoItem from "../components/TodoItem";
import IncrementButton from "../components/IncrementButton";
import "./SectionD.css";
import Lits from "../components/Lists";
import Inline from "../components/inline";

const SectionD = () => {
  const [search, setSearch] = useState("");
  const [todos, setTodos] = useState(["Task1", "Task2"]);
  const [num, setNum] = useState(10);
  const [theme, setTheme] = useState(false);
  const [count, setCount] = useState(0);

  const products = useMemo(() =>
    Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      name: "Product " + i
    })), []
  );

  const filtered = useMemo(() =>
    products.filter(p => p.name.includes(search)), [search, products]
  );

  const primes = useMemo(() => {
    let count = 0;
    for (let i = 2; i <= num; i++) {
      let prime = true;
      for (let j = 2; j < i; j++) {
        if (i % j === 0) prime = false;
      }
      if (prime) count++;
    }
    return count;
  }, [num]);

  const deleteTodo = useCallback((t) => {
    setTodos(prev => prev.filter(x => x !== t));
  }, []);

  const increment = useCallback(() => setCount(c => c + 1), []);

  return (
    <div>
      <h2 className="sectiond">Section D</h2>

      {/* Q12 */}
      <input onChange={e => setSearch(e.target.value)} />
      {filtered.slice(0, 5).map(p => <p key={p.id}>{p.name}</p>)}

      {/* Q13 */}
      <input type="number" onChange={e => setNum(+e.target.value)} />
      <p>Primes: {primes}</p>

      {/* Q14 */}
      {todos.map(t => <TodoItem key={t} todo={t} onDelete={deleteTodo} />)}

      {/* Q15 */}
      <IncrementButton onIncrement={increment} />
      <button onClick={() => setTheme(!theme)}>Toggle Theme</button>
      <p>{count}</p>
      <Lits primary={theme} />
      <Inline/>
    </div>
  );
};

export default SectionD;