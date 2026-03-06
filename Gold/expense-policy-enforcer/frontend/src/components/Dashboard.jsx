import React from 'react';

function Dashboard({ stats, onNewExpense, onViewExpenses, onViewPolicies }) {
  if (!stats) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600">Manage expenses and enforce policies</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-3xl font-bold text-amber-600">{stats.pending_count}</div>
          <div className="text-sm text-gray-600">Pending Approval</div>
        </div>
        <div className="card">
          <div className="text-3xl font-bold text-green-600">{stats.approved_count}</div>
          <div className="text-sm text-gray-600">Approved</div>
        </div>
        <div className="card">
          <div className="text-3xl font-bold text-red-600">{stats.rejected_count}</div>
          <div className="text-sm text-gray-600">Rejected</div>
        </div>
        <div className="card">
          <div className="text-3xl font-bold text-primary-600">${stats.this_month_amount}</div>
          <div className="text-sm text-gray-600">This Month</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={onNewExpense}
            className="btn-primary flex items-center justify-center space-x-2"
          >
            <span>📤</span>
            <span>Submit Expense</span>
          </button>
          <button
            onClick={onViewExpenses}
            className="btn-secondary flex items-center justify-center space-x-2"
          >
            <span>📋</span>
            <span>View Expenses</span>
          </button>
          <button
            onClick={onViewPolicies}
            className="btn-secondary flex items-center justify-center space-x-2"
          >
            <span>⚙️</span>
            <span>Manage Policies</span>
          </button>
        </div>
      </div>

      {/* Policy Reminders */}
      <div className="card bg-amber-50 border border-amber-200">
        <h3 className="text-lg font-semibold mb-2 text-amber-800">⚠️ Policy Reminders</h3>
        <ul className="space-y-1 text-amber-700">
          <li>• Expenses over $100 require manager approval</li>
          <li>• Receipts required for expenses over $25</li>
        </ul>
      </div>
    </div>
  );
}

export default Dashboard;
