import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, Outlet, useLocation, Navigate } from 'react-router-dom';
import { api, useAuth } from '../../utils/SectionDUtils';
import { motion } from 'framer-motion';
import { ArrowLeft, BookOpen, User as UserIcon, Settings, LogOut, Plus, Edit, Trash, Loader } from 'lucide-react';

// Q11: Multi-Page Blog
export const Q11Blog = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/posts?_limit=10').then(res => {
      setPosts(res.data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold gradient-text">Q11. Multi-Page Blog</h2>
      {loading ? <p>Loading posts...</p> : (
        <div className="grid gap-4">
          {posts.map(post => (
            <Link key={post.id} to={`/q11/post/${post.id}`} className="glass-card hover:border-primary/50 transition-all block">
              <h3 className="text-xl font-bold mb-2 capitalize">{post.title}</h3>
              <p className="text-muted text-sm line-clamp-2">{post.body}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export const Q11PostDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);

  useEffect(() => {
    api.get(`/posts/${id}`).then(res => setPost(res.data));
  }, [id]);

  if (!post) return <p>Loading post {id}...</p>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <button className="btn btn-outline" onClick={() => navigate('/q11')}><ArrowLeft size={18}/> Back to Blog</button>
      <div className="glass-card p-10">
        <h1 className="text-4xl font-bold mb-6 capitalize">{post.title}</h1>
        <p className="text-muted text-lg leading-relaxed">{post.body}</p>
      </div>
    </div>
  );
};

// Q12 Protected Routes & Dashboard
export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  if (!isAuthenticated) return <Navigate to="/q12/login" state={{ from: location }} replace />;
  return children;
};

export const Q12Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const from = location.state?.from?.pathname || "/q12/dashboard";

  return (
    <div className="max-w-md mx-auto py-20">
      <div className="glass-card space-y-6">
        <h2 className="text-3xl font-bold text-center">Secure Portal</h2>
        <div className="space-y-4">
          <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
          <input type="password" placeholder="Password" />
          <button className="btn btn-primary w-full py-4" onClick={() => { login({username}); navigate(from); }}>Sign In</button>
        </div>
      </div>
    </div>
  );
};

export const Q12Dashboard = () => {
  const { user, logout } = useAuth();
  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center mb-8 pb-4 border-b border-white/10">
        <h2 className="text-2xl font-bold">Welcome, {user?.username}</h2>
        <button className="btn btn-outline text-error border-error/20" onClick={logout}><LogOut size={18}/> Logout</button>
      </div>
      <div className="flex gap-4 mb-8">
        <Link to="/q12/dashboard/profile" className="btn btn-outline gap-2"><UserIcon size={18}/> Profile</Link>
        <Link to="/q12/dashboard/settings" className="btn btn-outline gap-2"><Settings size={18}/> Settings</Link>
      </div>
      <div className="flex-1 glass-card bg-white/5">
        <Outlet />
      </div>
    </div>
  );
};

// Q13 CRUD with Axios
export const Q13CRUD = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({ name: '', email: '' });

  const fetchUsers = async () => {
    setLoading(true);
    const res = await api.get('/users');
    setUsers(res.data);
    setLoading(false);
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (editingUser) {
        await api.put(`/users/${editingUser.id}`, { ...editingUser, ...formData });
        setUsers(users.map(u => u.id === editingUser.id ? { ...u, ...formData } : u));
      } else {
        const res = await api.post('/users', formData);
        setUsers([res.data, ...users]);
      }
      setFormData({ name: '', email: '' });
      setEditingUser(null);
    } catch (err) { alert("Error saving user"); }
    setIsSubmitting(false);
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure?")) return;
    try {
      await api.delete(`/users/${id}`);
      setUsers(users.filter(u => u.id !== id));
    } catch (err) { alert("Error deleting user"); }
  };

  return (
    <div className="grid lg:grid-cols-3 gap-8">
      <div className="lg:col-span-1">
        <div className="glass-card sticky top-8">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            {editingUser ? <Edit size={20}/> : <Plus size={20}/>}
            {editingUser ? 'Edit User' : 'Add New User'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input required placeholder="Full Name" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
            <input required type="email" placeholder="Email Address" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
            <div className="flex gap-2">
              <button className="btn btn-primary flex-1" disabled={isSubmitting}>
                {isSubmitting ? <Loader className="animate-spin" size={18}/> : editingUser ? 'Update' : 'Create'}
              </button>
              {editingUser && <button type="button" className="btn btn-outline" onClick={() => {setEditingUser(null); setFormData({name:'', email:''})}}>Cancel</button>}
            </div>
          </form>
        </div>
      </div>

      <div className="lg:col-span-2 space-y-4">
        <h3 className="text-xl font-bold flex justify-between items-center px-4">
          User Directory
          <span className="text-xs font-normal text-muted">{users.length} Total Users</span>
        </h3>
        {loading ? <p className="text-center py-20">Fetching users...</p> : (
          <div className="grid gap-3">
            {users.map(u => (
              <motion.div layout initial={{opacity:0}} animate={{opacity:1}} key={u.id} className="glass-card flex justify-between items-center group">
                <div>
                  <p className="font-bold">{u.name}</p>
                  <p className="text-xs text-muted">{u.email}</p>
                </div>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="p-2 hover:text-primary" onClick={() => {setEditingUser(u); setFormData({name:u.name, email:u.email})}}><Edit size={18}/></button>
                  <button className="p-2 hover:text-error" onClick={() => handleDelete(u.id)}><Trash size={18}/></button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
