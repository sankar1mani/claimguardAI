import React from 'react';

const AnalysisResults = ({ result }) => {
  if (!result) return null;

  const getStatusBadge = (status) => {
    const statusConfig = {
      'APPROVED': { color: 'success', icon: '✓', text: 'Approved' },
      'PARTIAL_APPROVAL': { color: 'warning', icon: '⚠', text: 'Partially Approved' },
      'REJECTED': { color: 'danger', icon: '✗', text: 'Rejected' }
    };

    const config = statusConfig[status] || statusConfig['REJECTED'];

    return (
      <div className={`inline-flex items-center gap-3 px-6 py-3 rounded-full badge-${config.color} text-xl font-bold`}>
        <span className="text-2xl">{config.icon}</span>
        {config.text}
      </div>
    );
  };

  const getItemStatusBadge = (status) => {
    if (status === 'APPROVED') {
      return <span className="badge badge-success text-xs">✓ Approved</span>;
    } else {
      return <span className="badge badge-danger text-xs">✗ Rejected</span>;
    }
  };

  const formatCurrency = (amount) => {
    return `₹${parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  // Calculate totals
  const totalClaimed = result.total_amount || result.subtotal || 0;
  const lineItems = result.line_items || [];
  
  // Calculate approved and rejected amounts from line items
  let totalApproved = 0;
  let totalRejected = 0;
  
  lineItems.forEach(item => {
    const price = item.total_price || 0;
    if (item.excluded || item.status === 'REJECTED') {
      totalRejected += price;
    } else {
      totalApproved += price;
    }
  });

  const approvalRate = totalClaimed > 0 ? (totalApproved / totalClaimed * 100) : 0;

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-slide-up">
      {/* Status Header */}
      <div className="card text-center">
        <div className="mb-4">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Claim Analysis Complete</h2>
          <p className="text-gray-600">Claim ID: {result.claim_id || 'N/A'}</p>
        </div>
        
        <div className="mb-6">
          {getStatusBadge(result.status || 'PARTIAL_APPROVAL')}
        </div>

        {/* Financial Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Total Claimed</p>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalClaimed)}</p>
          </div>
          <div className="bg-success-50 rounded-lg p-4">
            <p className="text-sm text-success-700 mb-1">Total Approved</p>
            <p className="text-2xl font-bold text-success-700">{formatCurrency(totalApproved)}</p>
          </div>
          <div className="bg-danger-50 rounded-lg p-4">
            <p className="text-sm text-danger-700 mb-1">Total Rejected</p>
            <p className="text-2xl font-bold text-danger-700">{formatCurrency(totalRejected)}</p>
          </div>
        </div>

        {/* Approval Rate Bar */}
        <div className="mt-6">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600">Approval Rate</span>
            <span className="font-bold text-gray-900">{approvalRate.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-success-500 h-3 rounded-full transition-all duration-1000"
              style={{ width: `${approvalRate}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Merchant Info */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Claim Details</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600">Merchant</p>
            <p className="font-semibold text-gray-900">{result.merchant_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Patient</p>
            <p className="font-semibold text-gray-900">{result.patient_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Date</p>
            <p className="font-semibold text-gray-900">{result.date || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Line Items Table */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Line Items Breakdown</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Item</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Qty</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Amount</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
              </tr>
            </thead>
            <tbody>
              {lineItems.map((item, index) => {
                const isRejected = item.excluded || item.status === 'REJECTED';
                return (
                  <tr
                    key={index}
                    className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                      isRejected ? 'bg-danger-50/50' : 'bg-success-50/20'
                    }`}
                  >
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium text-gray-900">{item.name}</p>
                        {item.category && (
                          <p className="text-xs text-gray-500">{item.category}</p>
                        )}
                        {isRejected && item.exclusion_reason && (
                          <p className="text-xs text-danger-600 mt-1">
                            ⚠ {item.exclusion_reason}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="text-center py-3 px-4 text-gray-700">
                      {item.quantity || 1}
                    </td>
                    <td className="text-right py-3 px-4 font-semibold text-gray-900">
                      {formatCurrency(item.total_price || 0)}
                    </td>
                    <td className="text-center py-3 px-4">
                      {getItemStatusBadge(isRejected ? 'REJECTED' : 'APPROVED')}
                    </td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot className="bg-gray-50">
              <tr>
                <td colSpan="2" className="py-4 px-4 text-right font-bold text-gray-900">
                  Total:
                </td>
                <td className="py-4 px-4 text-right font-bold text-xl text-gray-900">
                  {formatCurrency(totalClaimed)}
                </td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Excluded Items Summary */}
      {result.excluded_items_found && result.excluded_items_found.length > 0 && (
        <div className="card bg-danger-50 border-danger-200">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="font-bold text-danger-900 mb-2">Excluded Items Detected</h4>
              <p className="text-sm text-danger-800 mb-3">
                The following items were rejected based on policy exclusions:
              </p>
              <ul className="space-y-2">
                {result.excluded_items_found.map((item, index) => (
                  <li key={index} className="flex items-center justify-between bg-white rounded-lg p-3">
                    <div>
                      <p className="font-medium text-danger-900">{item.item_name}</p>
                      <p className="text-xs text-danger-700">{item.reason}</p>
                    </div>
                    <p className="font-bold text-danger-900">{formatCurrency(item.amount)}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Summary Note */}
      {result.reason && (
        <div className="card bg-primary-50 border-primary-200">
          <div className="flex items-start gap-3">
            <svg className="w-6 h-6 text-primary-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h4 className="font-bold text-primary-900 mb-1">Summary</h4>
              <p className="text-sm text-primary-800">{result.reason}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
