import React from 'react';

function ExpenseList({ expenses, onApprove, onReject, onBack }) {
  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-pending',
      approved: 'badge-approved',
      rejected: 'badge-rejected',
      needs_review: 'badge-needs-review',
    };
    return badges[status] || 'badge-pending';
  };

  const pendingExpenses = expenses.filter((e) => e.status === 'needs_review' || e.status === 'pending');
  const otherExpenses = expenses.filter((e) => e.status !== 'needs_review' && e.status !== 'pending');

  return (
    <div>
      <div className="mb-6">
        <button onClick={onBack} className="text-primary-600 hover:text-primary-700">
          ← Back to Dashboard
        </button>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-6">Expenses</h2>

      {/* Pending Approvals */}
      {pendingExpenses.length > 0 && (
        <div className="card mb-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <span className="text-amber-500 mr-2">⚠️</span>
            Pending Approval ({pendingExpenses.length})
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Employee
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Vendor
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Amount
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Date
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {pendingExpenses.map((expense) => (
                  <tr key={expense.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">User</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{expense.vendor}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      ${parseFloat(expense.amount).toFixed(2)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">{expense.date}</td>
                    <td className="px-4 py-3">
                      <span className={`badge ${getStatusBadge(expense.status)}`}>
                        {expense.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => onApprove(expense.id)}
                          className="text-green-600 hover:text-green-800 text-sm font-medium"
                        >
                          ✓ Approve
                        </button>
                        <button
                          onClick={() => onReject(expense.id)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium"
                        >
                          ✕ Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Other Expenses */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">All Expenses</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Vendor
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Category
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {expenses.map((expense) => (
                <tr key={expense.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">{expense.vendor}</td>
                  <td className="px-4 py-3 text-sm text-gray-500 capitalize">
                    {expense.category || '-'}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    ${parseFloat(expense.amount).toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{expense.date}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${getStatusBadge(expense.status)}`}>
                      {expense.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ExpenseList;
