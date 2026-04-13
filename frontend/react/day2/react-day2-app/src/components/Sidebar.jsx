import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, FormInput, Database, Cpu, 
  MapPin, Zap, Layers 
} from 'lucide-react';

const sections = [
  { id: 'section-a', name: 'A: Forms & State', icon: <FormInput size={20} />, questions: [1, 2, 3] },
  { id: 'section-b', name: 'B: Context & Reducer', icon: <Layers size={20} />, questions: [4, 5, 6] },
  { id: 'section-c', name: 'C: Hooks & Ref', icon: <Cpu size={20} />, questions: [7, 8, 9, 10] },
  { id: 'section-d', name: 'D: Routing & API', icon: <MapPin size={20} />, questions: [11, 12, 13] },
  { id: 'section-e', name: 'E: Optimization', icon: <Zap size={20} />, questions: [14, 15] },
  { id: 'section-f', name: 'F: Redux Toolkit', icon: <Database size={20} />, questions: [16, 17, 18, 19, 20] },
];

export const Sidebar = () => {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-900 text-white overflow-y-auto z-50">
      <div className="p-6">
        <h2 className="text-indigo-400 text-2xl font-bold">React Day 2</h2>
        <p className="text-slate-400 text-sm">20 Implementation Tasks</p>
      </div>
      <nav className="flex-1 px-4 pb-8">
        <NavLink to="/" className={({isActive}) => `flex items-center gap-3 p-3 rounded-lg mb-4 transition-all ${isActive ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' : 'text-slate-400 hover:bg-white/5'}`}>
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>

        {sections.map(section => (
          <div key={section.id} className="mb-6">
            <div className="flex items-center gap-2 px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {section.icon}
              {section.name}
            </div>
            <div className="flex flex-col gap-1">
              {section.questions.map(q => (
                <NavLink 
                  key={q} 
                  to={`/q${q}`}
                  className={({isActive}) => `px-3 py-2 rounded-md text-sm transition-all ${isActive ? 'bg-white/10 text-indigo-400 font-medium border-l-2 border-indigo-400' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                >
                  Question {q}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
};
