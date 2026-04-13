import React from 'react';
import { motion } from 'framer-motion';

export const Home = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-5xl font-extrabold mb-4">
          React <span className="gradient-text">Mastery</span> Day 2
        </h1>
        <p className="text-muted text-lg max-w-2xl mb-8">
          A comprehensive suite of 20 coding challenges covering everything from advanced forms 
          to Redux Toolkit and Performance optimization.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-left max-w-4xl">
          {[
            { title: 'Forms & Validation', desc: 'Manual validation, lifting state up, dynamic rendering.' },
            { title: 'State Management', desc: 'useReducer, Context API, Redux Toolkit.' },
            { title: 'Custom Hooks', desc: 'Building reusable logic for fetch, storage, and debouncing.' },
            { title: 'Routing & Auth', desc: 'Protected routes, nested routing, and fake JWT flows.' },
            { title: 'API Integration', desc: 'CRUD operations with Axios and async state handling.' },
            { title: 'Performance', desc: 'React.memo, useCallback, useMemo, and Error Boundaries.' },
          ].map((item, i) => (
            <motion.div 
              key={i}
              whileHover={{ scale: 1.05 }}
              className="glass-card p-6"
            >
              <h3 className="text-primary mb-2">{item.title}</h3>
              <p className="text-muted text-sm">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};
