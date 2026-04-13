import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './redux/store';
import { Sidebar } from './components/Sidebar';
import { AppProviders } from './context/SectionBContexts';
import { CartProvider } from './context/SectionBContexts';
import { AuthProvider } from './utils/SectionDUtils';
import { Home } from './pages/Home';

// Lazy loading all implementation components
const Q1 = lazy(() => import('./pages/SectionA/Questions').then(m => ({ default: m.Q1Form })));
const Q2 = lazy(() => import('./pages/SectionA/Questions').then(m => ({ default: m.Q2Temperature })));
const Q3 = lazy(() => import('./pages/SectionA/Questions').then(m => ({ default: m.Q3Survey })));

const Q4 = lazy(() => import('./pages/SectionB/Questions').then(m => ({ default: m.Q4Settings })));
const Q5 = lazy(() => import('./pages/SectionB/Questions').then(m => ({ default: m.Q5Cart })));
const Q6 = lazy(() => import('./pages/SectionB/Questions').then(m => ({ default: m.Q6MultiStep })));

const Q7Q9 = lazy(() => import('./pages/SectionC/Questions').then(m => ({ default: m.Q7Q9Search })));
const Q8 = lazy(() => import('./pages/SectionC/Questions').then(m => ({ default: m.Q8Notes })));
const Q10 = lazy(() => import('./pages/SectionC/Questions').then(m => ({ default: m.Q10Stopwatch })));

const Q11 = lazy(() => import('./pages/SectionD/Questions').then(m => ({ default: m.Q11Blog })));
const Q11Details = lazy(() => import('./pages/SectionD/Questions').then(m => ({ default: m.Q11PostDetails })));
const Q12Login = lazy(() => import('./pages/SectionD/Questions').then(m => ({ default: m.Q12Login })));
const Q12Dash = lazy(() => import('./pages/SectionD/Questions').then(m => ({ default: m.Q12Dashboard })));
const Q13 = lazy(() => import('./pages/SectionD/Questions').then(m => ({ default: m.Q13CRUD })));

const Q14_15 = lazy(() => import('./pages/SectionE/Questions').then(m => ({ default: m.Q15OptimizedList })));
const { ErrorBoundary, BuggyComponent } = lazy(() => import('./pages/SectionE/Questions').then(m => ({ default: { ErrorBoundary: m.ErrorBoundary, BuggyComponent: m.BuggyComponent } })));

const Q16 = lazy(() => import('./pages/SectionF/Questions').then(m => ({ default: m.Q16Counter })));
const Q17 = lazy(() => import('./pages/SectionF/Questions').then(m => ({ default: m.Q17Todo })));
const Q19 = lazy(() => import('./pages/SectionF/Questions').then(m => ({ default: m.Q19Users })));
const Q20 = lazy(() => import('./pages/SectionF/Questions').then(m => ({ default: m.Q20Cart })));

const { ProtectedRoute } = lazy(() => import('./pages/SectionD/Questions').then(m => ({ default: { ProtectedRoute: m.ProtectedRoute } })));

const LoadingFallback = () => (
  <div className="h-full w-full flex items-center justify-center">
    <div className="space-y-4 text-center">
      <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p className="text-gray-500 animate-pulse">Loading logic...</p>
    </div>
  </div>
);

function App() {
  return (
    <Provider store={store}>
      <AuthProvider>
        <AppProviders>
          <CartProvider>
            <Router>
              <Sidebar />
              <main className="ml-64 p-8 min-h-screen bg-gray-50">
                <Suspense fallback={<LoadingFallback />}>
                  <Routes>
                    <Route path="/" element={<Home />} />
                    
                    {/* Section A */}
                    <Route path="/q1" element={<Q1 />} />
                    <Route path="/q2" element={<Q2 />} />
                    <Route path="/q3" element={<Q3 />} />

                    {/* Section B */}
                    <Route path="/q4" element={<Q4 />} />
                    <Route path="/q5" element={<Q5 />} />
                    <Route path="/q6" element={<Q6 />} />

                    {/* Section C */}
                    <Route path="/q7" element={<Q7Q9 />} />
                    <Route path="/q8" element={<Q8 />} />
                    <Route path="/q9" element={<Q7Q9 />} />
                    <Route path="/q10" element={<Q10 />} />

                    {/* Section D */}
                    <Route path="/q11" element={<Q11 />} />
                    <Route path="/q11/post/:id" element={<Q11Details />} />
                    <Route path="/q12/login" element={<Q12Login />} />
                    <Route path="/q12/dashboard" element={
                      <ProtectedRoute>
                        <Q12Dash />
                      </ProtectedRoute>
                    }>
                      <Route path="profile" element={<div className="p-8"><h2>User Profile</h2><p>This is a nested protected route using Outlet.</p></div>} />
                      <Route path="settings" element={<div className="p-8"><h2>Account Settings</h2><p>Manage your preferences here.</p></div>} />
                      <Route index element={<div className="p-8"><p>Welcome to your secure dashboard. Choose an option below.</p></div>} />
                    </Route>
                    <Route path="/q13" element={<Q13 />} />

                    {/* Section E - Performance & Error Handling */}
                    <Route path="/q14" element={
                      <div className="space-y-12">
                         <h2 className="text-3xl font-bold">Q14. Error Boundary Demo</h2>
                         <p className="text-gray-600">The component below is wrapped in an Error Boundary.</p>
                         <ErrorBoundary>
                            <BuggyComponent />
                         </ErrorBoundary>
                      </div>
                    } />
                    <Route path="/q15" element={<Q14_15 />} />

                    {/* Section F - Redux */}
                    <Route path="/q16" element={<Q16 />} />
                    <Route path="/q17" element={<Q17 />} />
                    <Route path="/q18" element={<Navigate to="/q12/dashboard" replace />} />
                    <Route path="/q19" element={<Q19 />} />
                    <Route path="/q20" element={<Q20 />} />

                    <Route path="*" element={<div className="text-center py-20"><h1 className="text-6xl font-bold mb-4">404</h1><p>Task not implemented yet or wrong route.</p></div>} />
                  </Routes>
                </Suspense>
              </main>
            </Router>
          </CartProvider>
        </AppProviders>
      </AuthProvider>
    </Provider>
  );
}

export default App;