import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { 
  increment, decrement, incrementByAmount, reset,
  addTodo, removeTodo, toggleTodo, clearAll,
  fetchUsers,
  addToCart, removeFromCart, updateQty, clearCart
} from '../../redux/store';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Minus, RotateCcw, Trash2, Check, X, ShoppingCart, User, AlertCircle, RefreshCw } from 'lucide-react';

// Q16: Counter
export const Q16Counter = () => {
  const count = useSelector(state => state.counter.value);
  const dispatch = useDispatch();

  return (
    <div className="max-w-md mx-auto text-center space-y-8">
      <h2 className="text-3xl font-bold gradient-text">Q16. Redux Counter</h2>
      <div className="glass-card p-12">
        <div className="text-7xl font-bold mb-10 text-primary">{count}</div>
        <div className="grid grid-cols-2 gap-4">
          <button className="btn btn-primary" onClick={() => dispatch(increment())}><Plus size={20}/> increment</button>
          <button className="btn btn-primary" onClick={() => dispatch(decrement())}><Minus size={20}/> decrement</button>
          <button className="btn btn-outline" onClick={() => dispatch(incrementByAmount(5))}>+ 5</button>
          <button className="btn btn-outline text-error" onClick={() => dispatch(reset())}><RotateCcw size={18}/> Reset</button>
        </div>
      </div>
      <div className="glass-card bg-white/5 p-4 text-sm text-muted">
        This component and another could share this count: <strong>{count}</strong>
      </div>
    </div>
  );
};

// Q17: Todo List
export const Q17Todo = () => {
  const todos = useSelector(state => state.todos);
  const dispatch = useDispatch();
  const [text, setText] = useState('');

  const stats = {
    total: todos.length,
    completed: todos.filter(t => t.completed).length,
    pending: todos.filter(t => !t.completed).length
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="flex justify-between items-end">
        <h2 className="text-3xl font-bold gradient-text">Q17. Redux Todos</h2>
        <div className="flex gap-4">
          <div className="text-center bg-white/5 border border-white/10 px-4 py-2 rounded-xl">
            <p className="text-[10px] text-muted uppercase">Pending</p>
            <p className="font-bold text-secondary">{stats.pending}</p>
          </div>
          <div className="text-center bg-white/5 border border-white/10 px-4 py-2 rounded-xl">
            <p className="text-[10px] text-muted uppercase">Done</p>
            <p className="font-bold text-success">{stats.completed}</p>
          </div>
        </div>
      </div>

      <div className="glass-card flex gap-4">
        <input value={text} onChange={e => setText(e.target.value)} placeholder="What needs to be done?" onKeyPress={e => e.key === 'Enter' && (dispatch(addTodo(text)), setText(''))} />
        <button className="btn btn-primary" onClick={() => { if(text) { dispatch(addTodo(text)); setText(''); } }}><Plus size={18}/> Add</button>
      </div>

      <div className="space-y-3">
        <AnimatePresence>
          {todos.map(todo => (
            <motion.div initial={{opacity:0, y: 10}} animate={{opacity:1, y: 0}} exit={{opacity:0, scale: 0.9}} key={todo.id} className="glass-card flex items-center justify-between group">
              <div className="flex items-center gap-4">
                <button 
                  onClick={() => dispatch(toggleTodo(todo.id))}
                  className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${todo.completed ? 'bg-success border-success text-white' : 'border-white/20'}`}
                >
                  {todo.completed && <Check size={14}/>}
                </button>
                <span className={`${todo.completed ? 'text-muted line-through' : ''}`}>{todo.text}</span>
              </div>
              <button className="text-error/40 hover:text-error opacity-0 group-hover:opacity-100 transition-all" onClick={() => dispatch(removeTodo(todo.id))}><X size={18}/></button>
            </motion.div>
          ))}
        </AnimatePresence>
        {todos.length > 0 && <button className="text-xs text-muted hover:text-error w-full text-center py-4" onClick={() => dispatch(clearAll())}>Clear all tasks</button>}
      </div>
    </div>
  );
};

// Q19: Async Fetcher
export const Q19Users = () => {
  const { items, status, error } = useSelector(state => state.users);
  const dispatch = useDispatch();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold gradient-text">Q19. Async Thunk Users</h2>
        <button className="btn btn-outline gap-2" onClick={() => dispatch(fetchUsers())}>
          <RefreshCw size={18} className={status === 'loading' ? 'animate-spin' : ''}/> 
          Reload
        </button>
      </div>

      {status === 'loading' && <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">{[1,2,3,4,5,6].map(n => <div key={n} className="glass-card h-32 animate-pulse bg-white/5"></div>)}</div>}
      
      {status === 'failed' && (
        <div className="glass-card border-error/20 bg-error/5 p-8 text-center text-error space-y-3">
          <AlertCircle size={32} className="mx-auto"/>
          <p className="font-bold">Fetch Failed</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {status === 'succeeded' && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map(u => (
            <motion.div initial={{opacity:0}} animate={{opacity:1}} key={u.id} className="glass-card hover:border-primary/50 transition-colors">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary"><User size={20}/></div>
                <div>
                  <p className="font-bold">{u.name}</p>
                  <p className="text-xs text-muted">@{u.username}</p>
                </div>
              </div>
              <p className="text-sm text-muted mb-1">{u.email}</p>
              <p className="text-sm text-muted">{u.phone}</p>
            </motion.div>
          ))}
        </div>
      )}

      {status === 'idle' && (
        <div className="text-center py-20 bg-white/5 rounded-3xl border border-dashed border-white/10">
          <p className="text-muted mb-6">No users loaded yet.</p>
          <button className="btn btn-primary" onClick={() => dispatch(fetchUsers())}>Fetch Users Now</button>
        </div>
      )}
    </div>
  );
};

// Q20: Redux Cart
export const Q20Cart = () => {
  const cartItems = useSelector(state => state.cart.items);
  const dispatch = useDispatch();
  
  const products = [
    { id: 101, name: 'Redux Master Laptop', price: 1299, image: '💻' },
    { id: 102, name: 'State Management Pro Mouse', price: 89, image: '🖱️' },
    { id: 103, name: 'Toolkit mechanical Headset', price: 199, image: '🎧' },
  ];

  const total = cartItems.reduce((acc, item) => acc + item.price * item.qty, 0);

  return (
    <div className="grid lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 space-y-6">
        <h2 className="text-3xl font-bold gradient-text">Q20. Redux Toolkit Cart</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {products.map(p => (
            <div key={p.id} className="glass-card text-center group cursor-pointer" onClick={() => dispatch(addToCart(p))}>
              <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">{p.image}</div>
              <h4 className="font-bold mb-1">{p.name}</h4>
              <p className="text-primary font-bold mb-4">${p.price}</p>
              <button className="btn btn-outline text-xs w-full">Add to Cart</button>
            </div>
          ))}
        </div>
      </div>

      <div className="lg:col-span-1 glass-card flex flex-col min-h-[500px]">
        <h3 className="text-xl font-bold mb-8 flex items-center gap-2"><ShoppingCart size={22}/> Your Cart</h3>
        
        <div className="flex-1 space-y-4">
          <AnimatePresence>
            {cartItems.map(item => (
              <motion.div initial={{opacity:0, x: 20}} animate={{opacity:1, x:0}} exit={{opacity:0, x: -20}} key={item.id} className="flex justify-between items-center p-3 bg-white/5 rounded-xl border border-white/5">
                <div className="flex-1">
                  <p className="font-bold text-sm">{item.name}</p>
                  <p className="text-xs text-primary">${item.price}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center bg-black/20 rounded-lg">
                    <button className="p-1 px-2 hover:text-primary" onClick={() => dispatch(updateQty({id: item.id, change: -1}))}>-</button>
                    <span className="w-6 text-center text-sm font-bold">{item.qty}</span>
                    <button className="p-1 px-2 hover:text-primary" onClick={() => dispatch(updateQty({id: item.id, change: 1}))}>+</button>
                  </div>
                  <button className="text-error/40 hover:text-error" onClick={() => dispatch(removeFromCart(item.id))}><Trash2 size={18}/></button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {cartItems.length === 0 && <div className="text-center py-20 text-muted italic text-sm">Cart is empty implementation logic remains clean with RTK</div>}
        </div>

        <div className="pt-8 border-t border-white/10 mt-auto">
          <div className="flex justify-between text-2xl font-bold mb-6">
            <span>Total</span>
            <span className="text-primary">${total}</span>
          </div>
          <button className="btn btn-primary w-full py-4 rounded-2xl" disabled={cartItems.length === 0}>Complete Purchase</button>
        </div>
      </div>
    </div>
  );
};
