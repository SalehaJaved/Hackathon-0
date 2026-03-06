import React, { useState } from 'react';

function ExpenseForm({ onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    vendor: '',
    amount: '',
    date: new Date().toISOString().split('T')[0],
    category: 'general',
    notes: '',
  });
  const [receipt, setReceipt] = useState(null);
  const [preview, setPreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setReceipt(file);
      // Create preview for images
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => setPreview(reader.result);
        reader.readAsDataURL(file);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const submitData = new FormData();
    submitData.append('vendor', formData.vendor);
    submitData.append('amount', parseFloat(formData.amount));
    submitData.append('date', formData.date);
    submitData.append('category', formData.category);
    submitData.append('notes', formData.notes || '');
    if (receipt) {
      submitData.append('receipt', receipt);
    }

    await onSubmit(submitData);
    setSubmitting(false);
  };

  const categories = [
    { value: 'general', label: 'General' },
    { value: 'meals', label: 'Meals & Entertainment' },
    { value: 'travel', label: 'Travel' },
    { value: 'software', label: 'Software & Services' },
    { value: 'office_supplies', label: 'Office Supplies' },
    { value: 'fuel', label: 'Fuel' },
  ];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <button onClick={onCancel} className="text-primary-600 hover:text-primary-700">
          ← Back to Dashboard
        </button>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold mb-6">Submit Expense</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Receipt Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Receipt (Optional)
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                accept="image/*,.pdf"
                onChange={handleFileChange}
                className="hidden"
                id="receipt-upload"
              />
              <label htmlFor="receipt-upload" className="cursor-pointer">
                <div className="text-4xl mb-2">📎</div>
                <div className="text-sm text-gray-600">
                  {receipt ? receipt.name : 'Drop receipt here or click to browse'}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Supported: JPG, PNG, PDF (max 10MB)
                </div>
              </label>
              {preview && (
                <img src={preview} alt="Preview" className="mt-4 max-h-48 mx-auto rounded" />
              )}
            </div>
          </div>

          {/* Vendor */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Vendor *
            </label>
            <input
              type="text"
              name="vendor"
              value={formData.vendor}
              onChange={handleChange}
              required
              className="input-field"
              placeholder="e.g., Amazon Web Services"
            />
          </div>

          {/* Amount & Date */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Amount *
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-500">$</span>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleChange}
                  required
                  step="0.01"
                  min="0"
                  className="input-field pl-8"
                  placeholder="0.00"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date *
              </label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="input-field"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="input-field"
              placeholder="Additional details..."
            />
          </div>

          {/* Submit */}
          <div className="flex space-x-4 pt-4">
            <button
              type="submit"
              disabled={submitting}
              className="btn-primary flex-1"
            >
              {submitting ? 'Submitting...' : 'Submit Expense'}
            </button>
            <button type="button" onClick={onCancel} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ExpenseForm;
