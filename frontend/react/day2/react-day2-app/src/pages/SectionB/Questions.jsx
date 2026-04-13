import React, { useReducer } from 'react';
import { useTheme, useLanguage, useCart } from '../../context/SectionBContexts';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon, ShoppingBag, Plus, Minus, Trash2, ArrowRight, ArrowLeft, CheckCircle } from 'lucide-react';

// Q4 implementation
export const Q4Settings = () => {
  const { theme, setTheme } = useTheme();
  const { lang, setLang } = useLanguage();

  const translations = {
    en: { welcome: "Welcome to our Premium Dashboard", sub: "Everything is synced with Context API" },
    hi: { welcome: "हमारे प्रीमियम डैशबोर्ड में आपका स्वागत है", sub: "सब कुछ कॉन्टेक्स्ट एपीआई के साथ समन्वयित है" }
  };

  const DeepNested = () => {
    const { lang } = useLanguage();
    const { theme } = useTheme();
    return (
      <div className={`p-8 rounded-2xl border-2 border-dashed ${theme === 'dark' ? 'border-indigo-500/30 bg-indigo-500/5' : 'border-pink-500/30 bg-pink-500/5'}`}>
        <p className="text-xs text-slate-400 mb-2 font-mono">Deeply Nested Component (Level 4)</p>
        <h3 className="text-2xl mb-1">{translations[lang].welcome}</h3>
        <p className="text-slate-400">{translations[lang].sub}</p>
      </div>
    );
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h2 className="text-3xl font-bold gradient-text">Q4. Context Switchers</h2>
      <div className="glass-card flex justify-between items-center bg-slate-800/50 p-6 rounded-xl border border-white/10">
        <div className="flex gap-4">
          <button className={`btn gap-2 ${theme === 'light' ? 'bg-indigo-600 text-white' : 'border border-slate-700'}`} onClick={() => setTheme('light')}><Sun size={18}/> Light</button>
          <button className={`btn gap-2 ${theme === 'dark' ? 'bg-indigo-600 text-white' : 'border border-slate-700'}`} onClick={() => setTheme('dark')}><Moon size={18}/> Dark</button>
        </div>
        <div className="flex gap-2 p-1 bg-white/5 rounded-lg border border-white/10">
          <button className={`px-4 py-2 rounded-md transition-all ${lang === 'en' ? 'bg-indigo-600 text-white' : 'text-slate-400'}`} onClick={() => setLang('en')}>EN</button>
          <button className={`px-4 py-2 rounded-md transition-all ${lang === 'hi' ? 'bg-indigo-600 text-white' : 'text-slate-400'}`} onClick={() => setLang('hi')}>HI</button>
        </div>
      </div>
      <DeepNested />
    </div>
  );
};

// Q5 implementation
export const Q5Cart = () => {
  const { cart, dispatch, total, count } = useCart();
  const products = [
    { id: 1, name: 'Premium Wireless Headphones', price: 299, color: 'bg-indigo-500' },
    { id: 2, name: 'Minimalist Mechanical Keyboard', price: 159, color: 'bg-pink-500' },
    { id: 3, name: 'Ergonomic Standing Desk', price: 499, color: 'bg-cyan-500' },
  ];

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold gradient-text">Q5. Shopping Cart</h2>
          <p className="text-slate-400">useReducer + Context State Sharing</p>
        </div>
        <div className="glass-card flex items-center gap-3 px-6 py-3 bg-slate-800/50 rounded-xl border border-white/10">
          <ShoppingBag className="text-indigo-400" />
          <span className="font-bold text-xl">{count}</span>
          <span className="text-slate-400">items</span>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold px-2">Products</h3>
          {products.map(p => (
            <div key={p.id} className="glass-card flex justify-between items-center group hover:border-indigo-500/50 transition-colors bg-slate-800/30 p-4 rounded-xl border border-white/5">
              <div className="flex gap-4 items-center">
                <div className={`w-12 h-12 rounded-lg ${p.color} opacity-20 group-hover:opacity-40 transition-opacity`}></div>
                <div>
                  <h4 className="font-medium">{p.name}</h4>
                  <p className="text-indigo-400 font-bold">${p.price}</p>
                </div>
              </div>
              <button className="btn border border-slate-700 p-2 hover:bg-indigo-600 hover:text-white" onClick={() => dispatch({type: 'ADD', payload: p})}><Plus size={20}/></button>
            </div>
          ))}
        </div>

        <div className="glass-card flex flex-col min-h-[400px] bg-slate-800/30 p-6 rounded-xl border border-white/5">
          <h3 className="text-lg font-semibold mb-4 flex justify-between">
            Your Cart
            {cart.length > 0 && <button className="text-xs text-red-500 hover:underline" onClick={() => dispatch({type: 'CLEAR'})}>Clear All</button>}
          </h3>
          
          <div className="flex-1 space-y-4 mb-6">
            <AnimatePresence>
              {cart.map(item => (
                <motion.div initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }} key={item.id} className="flex justify-between items-center p-3 bg-white/5 rounded-xl border border-white/5">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{item.name}</p>
                    <p className="text-xs text-slate-400">${item.price} each</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center bg-black/20 rounded-lg p-1">
                      <button className="p-1 hover:text-indigo-400" onClick={() => dispatch({type: 'DEC', payload: item.id})}><Minus size={14}/></button>
                      <span className="w-8 text-center text-sm font-bold">{item.qty}</span>
                      <button className="p-1 hover:text-indigo-400" onClick={() => dispatch({type: 'INC', payload: item.id})}><Plus size={14}/></button>
                    </div>
                    <button className="text-red-400 hover:text-red-500 ml-2" onClick={() => dispatch({type: 'REMOVE', payload: item.id})}><Trash2 size={18}/></button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            {cart.length === 0 && <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-3 py-20"><ShoppingBag size={48} className="opacity-10"/><p>Cart is empty</p></div>}
          </div>

          <div className="pt-6 border-t border-white/10 mt-auto">
            <div className="flex justify-between text-xl font-bold mb-4">
              <span>Total</span>
              <span className="text-indigo-400">${total}</span>
            </div>
            <button className="btn bg-indigo-600 text-white w-full py-4 text-lg" disabled={cart.length === 0}>Checkout Now</button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Q6 Implementation
const stepReducer = (state, action) => {
  switch (action.type) {
    case 'SET_FIELD': return { ...state, data: { ...state.data, [action.field]: action.value } };
    case 'NEXT': return { ...state, step: state.step + 1 };
    case 'BACK': return { ...state, step: state.step - 1 };
    case 'RESET': return { step: 1, data: {} };
    default: return state;
  }
};

export const Q6MultiStep = () => {
  const [state, dispatch] = useReducer(stepReducer, { step: 1, data: { name: '', email: '', city: '', street: '', zip: '' } });

  const isStepValid = () => {
    if (state.step === 1) return state.data.name && state.data.email;
    if (state.step === 2) return state.data.city && state.data.street && state.data.zip;
    return true;
  };

  const StepIndicator = () => (
    <div className="flex justify-between mb-12 relative">
      <div className="absolute top-1/2 left-0 w-full h-0.5 bg-white/10 -translate-y-1/2 -z-10"></div>
      {[1, 2, 3].map(s => (
        <div key={s} className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${state.step >= s ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 border border-white/10'}`}>
          {state.step > s ? <CheckCircle size={20}/> : s}
        </div>
      ))}
    </div>
  );

  return (
    <div className="max-w-xl mx-auto py-10">
      <h2 className="text-3xl font-bold mb-4 gradient-text text-center">Q6. Multi-Step Form</h2>
      <StepIndicator />
      
      <div className="glass-card min-h-[300px] flex flex-col bg-slate-800/30 p-8 rounded-xl border border-white/10">
        {state.step === 1 && (
          <motion.div initial={{opacity: 0, x: 20}} animate={{opacity: 1, x: 0}} className="space-y-4">
            <h3 className="text-xl font-bold mb-4">Personal Info</h3>
            <div className="space-y-1">
              <label className="text-sm text-slate-400">Full Name</label>
              <input value={state.data.name} onChange={e => dispatch({type: 'SET_FIELD', field: 'name', value: e.target.value})} placeholder="John Doe" className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
            </div>
            <div className="space-y-1">
              <label className="text-sm text-slate-400">Email Address</label>
              <input value={state.data.email} onChange={e => dispatch({type: 'SET_FIELD', field: 'email', value: e.target.value})} placeholder="john@example.com" className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
            </div>
          </motion.div>
        )}

        {state.step === 2 && (
          <motion.div initial={{opacity: 0, x: 20}} animate={{opacity: 1, x: 0}} className="space-y-4">
            <h3 className="text-xl font-bold mb-4">Address Details</h3>
            <div className="space-y-1">
              <label className="text-sm text-slate-400">Street</label>
              <input value={state.data.street} onChange={e => dispatch({type: 'SET_FIELD', field: 'street', value: e.target.value})} placeholder="123 React Lane" className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm text-slate-400">City</label>
                <input value={state.data.city} onChange={e => dispatch({type: 'SET_FIELD', field: 'city', value: e.target.value})} placeholder="Webville" className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
              </div>
              <div className="space-y-1">
                <label className="text-sm text-slate-400">Zip Code</label>
                <input value={state.data.zip} onChange={e => dispatch({type: 'SET_FIELD', field: 'zip', value: e.target.value})} placeholder="10101" className="w-full bg-slate-800 border border-slate-700 rounded p-2" />
              </div>
            </div>
          </motion.div>
        )}

        {state.step === 3 && (
          <motion.div initial={{opacity: 0, x: 20}} animate={{opacity: 1, x: 0}} className="space-y-6">
            <h3 className="text-xl font-bold mb-4">Review & Submit</h3>
            <div className="bg-white/5 p-4 rounded-xl space-y-3">
              <p><strong>Name:</strong> {state.data.name}</p>
              <p><strong>Email:</strong> {state.data.email}</p>
              <p><strong>Address:</strong> {state.data.street}, {state.data.city} {state.data.zip}</p>
            </div>
            <p className="text-xs text-slate-400 italic">Click submit to finalize your registration.</p>
          </motion.div>
        )}

        <div className="flex justify-between mt-auto pt-8">
          <button className="btn border border-slate-700" disabled={state.step === 1} onClick={() => dispatch({type: 'BACK'})}><ArrowLeft size={18}/> Back</button>
          {state.step < 3 ? (
            <button className="btn bg-indigo-600 text-white" disabled={!isStepValid()} onClick={() => dispatch({type: 'NEXT'})}>Next <ArrowRight size={18}/></button>
          ) : (
            <button className="btn bg-indigo-600 text-white" onClick={() => alert('Data Submitted: ' + JSON.stringify(state.data))}>Submit Form</button>
          )}
        </div>
      </div>
    </div>
  );
};
