import { createSlice, configureStore, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Q16 Counter Slice
const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    increment: state => { state.value += 1; },
    decrement: state => { state.value -= 1; },
    incrementByAmount: (state, action) => { state.value += action.payload; },
    reset: state => { state.value = 0; }
  }
});

// Q17 Todo Slice
const todoSlice = createSlice({
  name: 'todos',
  initialState: [],
  reducers: {
    addTodo: (state, action) => { state.push({ id: Date.now(), text: action.payload, completed: false }); },
    removeTodo: (state, action) => state.filter(t => t.id !== action.payload),
    toggleTodo: (state, action) => {
      const todo = state.find(t => t.id === action.payload);
      if (todo) todo.completed = !todo.completed;
    },
    clearAll: () => []
  }
});

// Q18 Auth Slice
const authSlice = createSlice({
  name: 'auth',
  initialState: { 
    user: JSON.parse(localStorage.getItem('redux-user')) || null, 
    isAuthenticated: !!localStorage.getItem('redux-user') 
  },
  reducers: {
    login: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
      localStorage.setItem('redux-user', JSON.stringify(action.payload));
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      localStorage.removeItem('redux-user');
    }
  }
});

// Q19 Async Users Thunk
export const fetchUsers = createAsyncThunk('users/fetchUsers', async () => {
  const response = await axios.get('https://jsonplaceholder.typicode.com/users');
  return response.data;
});

const usersSlice = createSlice({
  name: 'users',
  initialState: { items: [], status: 'idle', error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => { state.status = 'loading'; })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  }
});

// Q20 Shopping Cart Slice
const cartSlice = createSlice({
  name: 'cart',
  initialState: { items: [] },
  reducers: {
    addToCart: (state, action) => {
      const existing = state.items.find(i => i.id === action.payload.id);
      if (existing) existing.qty += 1;
      else state.items.push({ ...action.payload, qty: 1 });
    },
    removeFromCart: (state, action) => {
      state.items = state.items.filter(i => i.id !== action.payload);
    },
    updateQty: (state, action) => {
      const { id, change } = action.payload;
      const item = state.items.find(i => i.id === id);
      if (item) item.qty = Math.max(1, item.qty + change);
    },
    clearCart: (state) => { state.items = []; }
  }
});

export const { increment, decrement, incrementByAmount, reset } = counterSlice.actions;
export const { addTodo, removeTodo, toggleTodo, clearAll } = todoSlice.actions;
export const { login, logout } = authSlice.actions;
export const { addToCart, removeFromCart, updateQty, clearCart } = cartSlice.actions;

export const store = configureStore({
  reducer: {
    counter: counterSlice.reducer,
    todos: todoSlice.reducer,
    auth: authSlice.reducer,
    users: usersSlice.reducer,
    cart: cartSlice.reducer
  }
});
