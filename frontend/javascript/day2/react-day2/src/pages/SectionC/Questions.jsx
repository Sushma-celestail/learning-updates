import React, { useState, useRef, useEffect } from 'react';
import { useFetch, useLocalStorage, useDebounce } from '../../hooks/SectionCHooks';
import { motion } from 'framer-motion';
import { Search, RotateCcw, Play, Pause, List, Save, User, FileText } from 'lucide-react';

// Q7 & Q9 Search with Debounce and Fetch
export const Q7Q9Search = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);
  const { data, loading, error, refetch } = useFetch(`https://jsonplaceholder.typicode.com/users?q=${debouncedSearch}`);

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold gradient-text">Q7 & Q9. useFetch + useDebounce</h2>
          <p className="text-muted">Search API with 500ms delay & fetch state handling</p>
        </div>
        <button className="btn btn-outline" onClick={() => refetch()}><RotateCcw size={18}/> Refresh</button>
      </div>

      <div className="relative max-w-lg">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted" size={20}/>
        <input 
          type="text" 
          value={searchTerm} 
          onChange={e => setSearchTerm(e.target.value)} 
          placeholder="Search users..." 
          className="pl-12 py-4"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading && [1,2,3].map(n => <div key={n} className="glass-card h-32 animate-pulse bg-white/5"></div>)}
        {error && <div className="col-span-full text-error p-4 bg-error/10 rounded-xl border border-error/20">Error: {error}</div>}
        {data && data.map(user => (
          <motion.div initial={{opacity: 0, scale: 0.9}} animate={{opacity: 1, scale: 1}} key={user.id} className="glass-card flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">{user.name[0]}</div>
            <div>
              <p className="font-medium">{user.name}</p>
              <p className="text-xs text-muted">{user.email}</p>
            </div>
          </motion.div>
        ))}
        {data?.length === 0 && !loading && <div className="col-span-full text-center py-10 text-muted">No results found for "{searchTerm}"</div>}
      </div>
    </div>
  );
};

// Q8 Notes App with useLocalStorage
export const Q8Notes = () => {
  const [notes, setNotes] = useLocalStorage('app-notes', []);
  const [inputValue, setInputValue] = useState('');

  const addNote = () => {
    if (!inputValue.trim()) return;
    setNotes([...notes, { id: Date.now(), text: inputValue, date: new Date().toLocaleString() }]);
    setInputValue('');
  };

  const deleteNote = (id) => setNotes(notes.filter(n => n.id !== id));

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-3xl font-bold gradient-text">Q8. Persisted Notes</h2>
      <div className="glass-card flex gap-4">
        <input value={inputValue} onChange={e => setInputValue(e.target.value)} placeholder="Type a note..." onKeyPress={e => e.key === 'Enter' && addNote()} />
        <button className="btn btn-primary" onClick={addNote}><Save size={18}/> Add</button>
      </div>
      <div className="grid gap-4">
        {notes.map(note => (
          <motion.div initial={{opacity: 0, y: 10}} animate={{opacity: 1, y: 0}} key={note.id} className="glass-card flex justify-between items-start group">
            <div>
              <p className="mb-1">{note.text}</p>
              <p className="text-[10px] text-muted uppercase tracking-wider">{note.date}</p>
            </div>
            <button className="text-error opacity-0 group-hover:opacity-100 transition-opacity" onClick={() => deleteNote(note.id)}>Delete</button>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

// Q10 Stopwatch with useRef
export const Q10Stopwatch = () => {
  const [time, setTime] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [laps, setLaps] = useState([]);
  const intervalRef = useRef(null);

  const start = () => {
    if (isRunning) return;
    setIsRunning(true);
    intervalRef.current = setInterval(() => {
      setTime(prev => prev + 10);
    }, 10);
  };

  const pause = () => {
    clearInterval(intervalRef.current);
    setIsRunning(false);
  };

  const reset = () => {
    pause();
    setTime(0);
    setLaps([]);
  };

  const lap = () => {
    setLaps([{ id: Date.now(), time }, ...laps]);
  };

  const formatTime = (ms) => {
    const mins = Math.floor(ms / 60000).toString().padStart(2, '0');
    const secs = Math.floor((ms % 60000) / 1000).toString().padStart(2, '0');
    const msecs = Math.floor((ms % 1000) / 10).toString().padStart(2, '0');
    return `${mins}:${secs}:${msecs}`;
  };

  return (
    <div className="max-w-xl mx-auto py-10 flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-10 gradient-text">Q10. useRef Stopwatch</h2>
      
      <div className="relative mb-12">
        <div className="text-7xl font-mono font-bold tracking-tighter tabular-nums bg-white/5 px-10 py-8 rounded-3xl border border-white/10 shadow-2xl">
          {formatTime(time)}
        </div>
        {isRunning && <motion.div animate={{scale: [1, 1.2, 1], opacity: [0.3, 0.1, 0.3]}} transition={{repeat: Infinity, duration: 1}} className="absolute -inset-4 bg-primary rounded-full -z-10 blur-2xl"></motion.div>}
      </div>

      <div className="flex gap-4 mb-12">
        {!isRunning ? (
          <button className="btn btn-primary px-8" onClick={start}><Play size={20}/> Start</button>
        ) : (
          <button className="btn btn-outline border-secondary text-secondary px-8" onClick={pause}><Pause size={20}/> Pause</button>
        )}
        <button className="btn btn-outline px-8" onClick={lap} disabled={time === 0}><List size={20}/> Lap</button>
        <button className="btn btn-outline text-error border-error/30 px-8" onClick={reset} disabled={time === 0 && !isRunning}><RotateCcw size={20}/> Reset</button>
      </div>

      <div className="w-full glass-card max-h-60 overflow-y-auto space-y-2">
        <h3 className="text-sm font-bold text-muted uppercase tracking-widest px-2 mb-4">Lap History</h3>
        {laps.map((l, i) => (
          <div key={l.id} className="flex justify-between p-3 rounded-lg bg-white/5 border border-white/5">
            <span className="text-muted">Lap {laps.length - i}</span>
            <span className="font-mono font-bold text-primary">{formatTime(l.time)}</span>
          </div>
        ))}
        {laps.length === 0 && <p className="text-center py-8 text-muted text-sm italic">No laps recorded</p>}
      </div>
    </div>
  );
};
