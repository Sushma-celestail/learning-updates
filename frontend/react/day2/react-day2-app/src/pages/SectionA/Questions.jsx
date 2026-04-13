import React, { useState } from 'react';
import { motion } from 'framer-motion';

// Q1: Multi-Field Registration Form
export const Q1Form = () => {
  const [formData, setFormData] = useState({
    name: '', email: '', password: '', confirmPassword: '', age: '', gender: ''
  });
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  const validate = () => {
    let newErrors = {};
    if (!formData.name) newErrors.name = "Name is required";
    if (!formData.email || !/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = "Valid email is required";
    if (formData.password.length < 8 || !/(?=.*[0-9])(?=.*[!@#$%^&*])/.test(formData.password)) {
      newErrors.password = "Password must be >= 8 chars with a number and special char";
    }
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "Passwords must match";
    if (formData.age < 18 || formData.age > 100) newErrors.age = "Age must be between 18 and 100";
    if (!formData.gender) newErrors.gender = "Gender is required";
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) setSuccess(true);
  };

  if (success) {
    return (
      <motion.div initial={{scale: 0.9, opacity: 0}} animate={{scale: 1, opacity: 1}} className="glass-card max-w-md mx-auto p-10 text-center">
        <div className="text-emerald-500 text-5xl mb-4">✓</div>
        <h2 className="text-2xl mb-4">Registration Successful!</h2>
        <div className="text-left space-y-2 text-slate-400">
          <p><strong>Name:</strong> {formData.name}</p>
          <p><strong>Email:</strong> {formData.email}</p>
          <p><strong>Age:</strong> {formData.age}</p>
          <p><strong>Gender:</strong> {formData.gender}</p>
        </div>
        <button className="btn btn-primary mt-6 w-full" onClick={() => {setSuccess(false); setFormData({name:'',email:'',password:'',confirmPassword:'',age:'',gender:''})}}>Reset Form</button>
      </motion.div>
    );
  }

  return (
    <div className="max-w-xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 gradient-text">Q1. Registration Form</h2>
      <form onSubmit={handleSubmit} className="glass-card space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Name</label>
            <input type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
            {errors.name && <p className="text-red-500 text-xs">{errors.name}</p>}
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Email</label>
            <input type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
            {errors.email && <p className="text-red-500 text-xs">{errors.email}</p>}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Password</label>
            <input type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
            {errors.password && <p className="text-red-500 text-xs">{errors.password}</p>}
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Confirm Password</label>
            <input type="password" value={formData.confirmPassword} onChange={e => setFormData({...formData, confirmPassword: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
            {errors.confirmPassword && <p className="text-red-500 text-xs">{errors.confirmPassword}</p>}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-sm font-medium">Age</label>
            <input type="number" value={formData.age} onChange={e => setFormData({...formData, age: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
            {errors.age && <p className="text-red-500 text-xs">{errors.age}</p>}
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium">Gender</label>
            <select value={formData.gender} onChange={e => setFormData({...formData, gender: e.target.value})} className="w-full bg-slate-800 border border-slate-700 rounded p-2">
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            {errors.gender && <p className="text-red-500 text-xs">{errors.gender}</p>}
          </div>
        </div>
        <button type="submit" className="btn btn-primary w-full mt-4">Register Account</button>
      </form>
    </div>
  );
};

// Q2: Temperature Converter (Lifting State Up)
export const Q2Temperature = () => {
  const [celsius, setCelsius] = useState('');
  const [fahrenheit, setFahrenheit] = useState('');

  const toF = (c) => (c * 9/5 + 32).toFixed(2);
  const toC = (f) => ((f - 32) * 5/9).toFixed(2);

  const handleCChange = (val) => {
    setCelsius(val);
    setFahrenheit(val === '' ? '' : toF(val));
  };

  const handleFChange = (val) => {
    setFahrenheit(val);
    setCelsius(val === '' ? '' : toC(val));
  };

  const getWaterState = (c) => {
    if (c === '') return 'N/A';
    if (c <= 0) return 'FREEZE';
    if (c >= 100) return 'BOIL';
    return 'be LIQUID';
  };

  return (
    <div className="max-w-xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 gradient-text">Q2. Temperature Converter</h2>
      <div className="glass-card flex flex-col gap-6 p-8">
        <div className="flex gap-4">
          <div className="flex-1 space-y-2">
            <label className="text-sm font-medium text-slate-400">Celsius (°C)</label>
            <input type="number" value={celsius} onChange={e => handleCChange(e.target.value)} placeholder="0" className="w-full text-2xl text-center py-4 bg-slate-800 border border-slate-700 rounded" />
          </div>
          <div className="flex-1 space-y-2">
            <label className="text-sm font-medium text-slate-400">Fahrenheit (°F)</label>
            <input type="number" value={fahrenheit} onChange={e => handleFChange(e.target.value)} placeholder="32" className="w-full text-2xl text-center py-4 bg-slate-800 border border-slate-700 rounded" />
          </div>
        </div>
        <div className="text-center p-6 bg-white/5 rounded-xl border border-white/10">
          <p className="text-slate-400 text-sm uppercase tracking-widest mb-2 font-semibold">Water State</p>
          <p className={`text-4xl font-bold ${celsius >= 100 ? 'text-pink-500' : celsius <= 0 ? 'text-cyan-400' : 'text-emerald-500'}`}>
            {getWaterState(celsius)}
          </p>
        </div>
      </div>
    </div>
  );
};

// Q3: Dynamic Survey Form Builder
export const Q3Survey = () => {
  const config = [
    { name: 'fullName', label: 'Full Name', type: 'text', required: true },
    { name: 'contactEmail', label: 'Work Email', type: 'email', required: true },
    { name: 'experience', label: 'Years of Experience', type: 'number', required: false },
    { name: 'role', label: 'Current Role', type: 'select', options: ['Developer', 'Designer', 'Manager', 'Other'], required: true },
    { name: 'newsletter', label: 'Subscribe to newsletter', type: 'checkbox', required: false }
  ];

  const [responses, setResponses] = useState({});
  const [submittedData, setSubmittedData] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmittedData(responses);
  };

  return (
    <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
      <div>
        <h2 className="text-3xl font-bold mb-6 gradient-text">Q3. Dynamic Survey</h2>
        <form onSubmit={handleSubmit} className="glass-card space-y-5">
          {config.map(field => (
            <div key={field.name} className="space-y-1">
              <label className="text-sm font-medium">
                {field.label} {field.required && <span className="text-red-500">*</span>}
              </label>
              {field.type === 'select' ? (
                <select 
                  required={field.required}
                  value={responses[field.name] || ''} 
                  onChange={e => setResponses({...responses, [field.name]: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded p-2"
                >
                  <option value="">Choose one...</option>
                  {field.options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                </select>
              ) : field.type === 'checkbox' ? (
                <input 
                  type="checkbox" 
                  className="w-5 h-5 block" 
                  checked={responses[field.name] || false}
                  onChange={e => setResponses({...responses, [field.name]: e.target.checked})}
                />
              ) : (
                <input 
                  type={field.type}
                  required={field.required}
                  value={responses[field.name] || ''}
                  onChange={e => setResponses({...responses, [field.name]: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded p-2"
                />
              )}
            </div>
          ))}
          <button type="submit" className="btn btn-primary w-full mt-4">Submit Survey</button>
        </form>
      </div>

      <div className="space-y-6">
        <h3 className="text-xl font-semibold text-slate-400">JSON Result</h3>
        <div className="glass-card bg-slate-900 font-mono text-sm overflow-hidden p-6">
          <pre className="text-cyan-400">
            {JSON.stringify(submittedData || responses, null, 2)}
          </pre>
        </div>
        {!submittedData && <p className="text-xs text-slate-500 italic">* Showing live state before submit</p>}
      </div>
    </div>
  );
};
