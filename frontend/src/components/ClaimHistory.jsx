import React, { useEffect, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ClaimHistory = ({ onViewClaim }) => {
    const [claims, setClaims] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchClaims = async () => {
        try {
            const response = await fetch(`${API_URL}/api/claims`);
            if (response.ok) {
                const data = await response.json();
                setClaims(data);
            }
        } catch (error) {
            console.error("Failed to fetch history:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClaims();
        // Poll every 10s to keep updated
        const interval = setInterval(fetchClaims, 10000);
        return () => clearInterval(interval);
    }, []);

    const formatDate = (isoString) => {
        return new Date(isoString).toLocaleDateString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric'
        });
    };

    const formatCurrency = (amount) => {
        return `₹${parseFloat(amount).toLocaleString('en-IN')}`;
    };

    if (loading) return (
        <div className="mt-8 text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200 animate-pulse">
            <div className="text-gray-400">Loading claim history...</div>
        </div>
    );

    if (claims.length === 0) return (
        <div className="mt-8 text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No claims found</h3>
            <p className="mt-1 text-sm text-gray-500">Upload a receipt to generate your first claim record.</p>
        </div>
    );

    return (
        <div className="card mt-8 animate-fade-in">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900">Recent Claims History</h3>
                <button
                    onClick={fetchClaims}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                    Refresh
                </button>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="bg-gray-50 border-b border-gray-200">
                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Date</th>
                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Merchant</th>
                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Patient</th>
                            <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Amount</th>
                            <th className="text-center py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Status</th>
                            <th className="text-right py-3 px-4 text-xs font-semibold text-gray-600 uppercase">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {claims.map((claim) => (
                            <tr key={claim.id} className="hover:bg-gray-50 transition-colors">
                                <td className="py-3 px-4 text-sm text-gray-600">
                                    {formatDate(claim.created_at)}
                                </td>
                                <td className="py-3 px-4 text-sm font-medium text-gray-900">
                                    {claim.merchant_name || 'Unknown'}
                                </td>
                                <td className="py-3 px-4 text-sm text-gray-600">
                                    {claim.patient_name || 'Unknown'}
                                </td>
                                <td className="py-3 px-4 text-right text-sm font-medium text-gray-900">
                                    {formatCurrency(claim.total_claimed)}
                                </td>
                                <td className="py-3 px-4 text-center">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    ${claim.status === 'APPROVED' ? 'bg-success-100 text-success-800' :
                                            claim.status === 'REJECTED' ? 'bg-danger-100 text-danger-800' :
                                                'bg-warning-100 text-warning-800'}`}>
                                        {claim.status}
                                    </span>
                                </td>
                                <td className="py-3 px-4 text-right">
                                    <button
                                        onClick={() => onViewClaim(claim.full_data)}
                                        className="text-primary-600 hover:text-primary-800 text-sm font-semibold hover:underline"
                                    >
                                        View Report
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ClaimHistory;
