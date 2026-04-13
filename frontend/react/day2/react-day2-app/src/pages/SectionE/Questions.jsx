import React, { Component, memo, useMemo, useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Heart, Search } from 'lucide-react';

// Q14: Error Boundary
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) {
      return (
        <div className="glass-card border-red-500/20 bg-red-500/5 p-12 text-center space-y-4 rounded-xl border border-white/5">
          <AlertTriangle size={48} className="text-red-500 mx-auto"/>
          <h3 className="text-2xl font-bold">Something went wrong.</h3>
          <p className="text-slate-400">This component encountered a runtime error.</p>
          <button className="btn bg-indigo-600 text-white" onClick={() => this.setState({ hasError: false })}>
            <RefreshCw size={18}/> Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export const BuggyComponent = () => {
  const [shouldError, setShouldError] = useState(false);
  if (shouldError) throw new Error("I crashed!");
  return (
    <div className="glass-card p-8 text-center bg-indigo-500/10 rounded-xl border border-white/5">
      <h4 className="mb-4">This component can crash</h4>
      <button className="btn bg-red-600 text-white" onClick={() => setShouldError(true)}>Trigger Crash</button>
    </div>
  );
};

// Q15: Optimized Card
const UserCard = memo(({ user, onLike }) => {
  console.log(`Rendering Card: ${user.name}`);
  return (
    <div className="glass-card flex justify-between items-center group bg-slate-800/30 p-4 rounded-xl border border-white/5">
      <div>
        <p className="font-bold">{user.name}</p>
        <p className="text-xs text-slate-400">Likes: {user.likes}</p>
      </div>
      <button className="p-3 rounded-full hover:bg-pink-500/10 text-pink-500 transition-colors" onClick={() => onLike(user.id)}>
        <Heart size={20} fill={user.likes > 0 ? "currentColor" : "none"}/>
      </button>
    </div>
  );
});

export const Q15OptimizedList = () => {
  const [search, setSearch] = useState('');
  const [users, setUsers] = useState(() => 
    Array.from({ length: 1000 }, (_, i) => ({ id: i, name: `User ${i + 1}`, likes: 0 }))
  );

  const handleLike = useCallback((id) => {
    setUsers(prev => prev.map(u => u.id === id ? { ...u, likes: u.likes + 1 } : u));
  }, []);

  const filteredUsers = useMemo(() => {
    console.log("Filtering 1000 users...");
    return users.filter(u => u.name.toLowerCase().includes(search.toLowerCase())).slice(0, 20);
  }, [users, search]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold gradient-text">Q15. Performance Optimization</h2>
          <p className="text-slate-400">Memoized cards, callback handlers, and memoized filtering of 1000 users.</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18}/>
          <input className="pl-10 w-64 bg-slate-800 border border-slate-700 rounded p-2" placeholder="Filter 1000 users..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {filteredUsers.map(u => (
          <UserCard key={u.id} user={u} onLike={handleLike} />
        ))}
      </div>
      <p className="text-xs text-slate-500 italic text-center">Open console to see render logs. Only the liked card re-renders.</p>
    </div>
  );
};
