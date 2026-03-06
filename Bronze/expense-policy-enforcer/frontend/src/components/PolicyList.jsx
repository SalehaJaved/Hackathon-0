import React from 'react';

function PolicyList({ policies, onToggle, onBack }) {
  return (
    <div>
      <div className="mb-6">
        <button onClick={onBack} className="text-primary-600 hover:text-primary-700">
          ← Back to Dashboard
        </button>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-6">Policy Management</h2>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Active Policies</h3>
        <div className="space-y-4">
          {policies.map((policy) => (
            <div
              key={policy.id}
              className={`border rounded-lg p-4 ${
                policy.active ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">
                      {policy.active ? '🟢' : '⚪'}
                    </span>
                    <h4 className="font-semibold text-gray-900">{policy.name}</h4>
                  </div>
                  {policy.description && (
                    <p className="text-sm text-gray-600 mt-1">{policy.description}</p>
                  )}
                  <div className="mt-2 text-xs text-gray-500">
                    <span className="inline-block bg-gray-200 px-2 py-1 rounded mr-2">
                      {policy.condition_type.replace('_', ' ')}
                    </span>
                    <span className="inline-block bg-primary-100 text-primary-800 px-2 py-1 rounded">
                      {policy.action.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => onToggle(policy.id)}
                  className={`px-3 py-1 rounded text-sm font-medium ${
                    policy.active
                      ? 'bg-red-100 text-red-700 hover:bg-red-200'
                      : 'bg-green-100 text-green-700 hover:bg-green-200'
                  }`}
                >
                  {policy.active ? 'Disable' : 'Enable'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {policies.length === 0 && (
          <p className="text-gray-500 text-center py-8">No policies configured</p>
        )}
      </div>

      {/* Policy Info */}
      <div className="card mt-6 bg-blue-50 border border-blue-200">
        <h3 className="text-lg font-semibold mb-2 text-blue-800">ℹ️ About Policies</h3>
        <p className="text-blue-700 text-sm">
          Policies are automatically enforced when expenses are submitted. 
          Expenses that violate policies are flagged for manager approval or auto-rejected.
        </p>
      </div>
    </div>
  );
}

export default PolicyList;
