import React, { useState, useEffect } from 'react';
import { expensesApi, policiesApi } from './api/client';
import Dashboard from './components/Dashboard';
import ExpenseForm from './components/ExpenseForm';
import ExpenseList from './components/ExpenseList';
import PolicyList from './components/PolicyList';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Load initial data
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, expensesData, policiesData] = await Promise.all([
        expensesApi.getStats(),
        expensesApi.list(),
        policiesApi.list(),
      ]);
      setStats(statsData);
      setExpenses(expensesData);
      setPolicies(policiesData);
    } catch (error) {
      console.error('Failed to load data:', error);
      showNotification('Failed to load data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleExpenseSubmit = async (formData) => {
    try {
      const result = await expensesApi.submit(formData);
      showNotification(result.message);
      loadData();
      setCurrentView('dashboard');
    } catch (error) {
      showNotification(error.response?.data?.detail || 'Failed to submit expense', 'error');
    }
  };

  const handleApprove = async (id) => {
    try {
      await expensesApi.approve(id);
      showNotification('Expense approved');
      loadData();
    } catch (error) {
      showNotification('Failed to approve expense', 'error');
    }
  };

  const handleReject = async (id) => {
    try {
      await expensesApi.reject(id, 'Rejected by manager');
      showNotification('Expense rejected');
      loadData();
    } catch (error) {
      showNotification('Failed to reject expense', 'error');
    }
  };

  const handleTogglePolicy = async (id) => {
    try {
      await policiesApi.toggle(id);
      showNotification('Policy updated');
      loadData();
    } catch (error) {
      showNotification('Failed to update policy', 'error');
    }
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <Dashboard
            stats={stats}
            onNewExpense={() => setCurrentView('submit')}
            onViewExpenses={() => setCurrentView('expenses')}
            onViewPolicies={() => setCurrentView('policies')}
          />
        );
      case 'submit':
        return (
          <ExpenseForm
            onSubmit={handleExpenseSubmit}
            onCancel={() => setCurrentView('dashboard')}
          />
        );
      case 'expenses':
        return (
          <ExpenseList
            expenses={expenses}
            onApprove={handleApprove}
            onReject={handleReject}
            onBack={() => setCurrentView('dashboard')}
          />
        );
      case 'policies':
        return (
          <PolicyList
            policies={policies}
            onToggle={handleTogglePolicy}
            onBack={() => setCurrentView('dashboard')}
          />
        );
      default:
        return <Dashboard stats={stats} onNewExpense={() => setCurrentView('submit')} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <span className="text-2xl mr-2">💳</span>
              <h1 className="text-xl font-bold text-gray-900">
                Expense Policy Enforcer
              </h1>
            </div>
            <nav className="flex space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  currentView === 'dashboard'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('expenses')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  currentView === 'expenses'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Expenses
              </button>
              <button
                onClick={() => setCurrentView('policies')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  currentView === 'policies'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Policies
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Notification */}
      {notification && (
        <div className="fixed top-4 right-4 z-50">
          <div
            className={`px-4 py-2 rounded-lg shadow-lg ${
              notification.type === 'error'
                ? 'bg-red-500 text-white'
                : 'bg-green-500 text-white'
            }`}
          >
            {notification.message}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          renderView()
        )}
      </main>
    </div>
  );
}

export default App;
