import React from 'react';

const FraudDetectionCard = ({ fraudDetection }) => {
    if (!fraudDetection) return null;

    const {
        suspicious = false,
        fraud_indicators = [],
        confidence_score = 1.0,
        recommendation = 'APPROVE'
    } = fraudDetection;

    // Determine risk level based on recommendation and confidence
    const getRiskLevel = () => {
        if (recommendation === 'REJECT') return 'HIGH';
        if (recommendation === 'MANUAL_REVIEW' || suspicious) return 'MEDIUM';
        return 'LOW';
    };

    const riskLevel = getRiskLevel();

    // Risk level configurations
    const riskConfig = {
        HIGH: {
            color: 'danger',
            bgColor: 'bg-danger-50',
            borderColor: 'border-danger-300',
            textColor: 'text-danger-900',
            icon: '🚨',
            label: 'High Risk',
            description: 'Significant fraud indicators detected'
        },
        MEDIUM: {
            color: 'warning',
            bgColor: 'bg-warning-50',
            borderColor: 'border-warning-300',
            textColor: 'text-warning-900',
            icon: '⚠️',
            label: 'Medium Risk',
            description: 'Manual review recommended'
        },
        LOW: {
            color: 'success',
            bgColor: 'bg-success-50',
            borderColor: 'border-success-300',
            textColor: 'text-success-900',
            icon: '✅',
            label: 'Low Risk',
            description: 'No significant fraud indicators'
        }
    };

    const config = riskConfig[riskLevel];
    const confidencePercentage = (confidence_score * 100).toFixed(1);

    return (
        <div className={`card ${config.bgColor} ${config.borderColor} border-2`}>
            <div className="flex items-start gap-4">
                {/* Icon */}
                <div className="flex-shrink-0">
                    <div className={`w-16 h-16 rounded-full ${config.bgColor} flex items-center justify-center text-3xl border-2 ${config.borderColor}`}>
                        {config.icon}
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1">
                    <div className="flex items-center justify-between mb-3">
                        <div>
                            <h3 className={`text-xl font-bold ${config.textColor} mb-1`}>
                                Fraud Detection Analysis
                            </h3>
                            <p className="text-sm text-gray-600">{config.description}</p>
                        </div>
                        <div className={`px-4 py-2 rounded-full badge-${config.color} font-bold`}>
                            {config.label}
                        </div>
                    </div>

                    {/* Confidence Score */}
                    <div className="mb-4">
                        <div className="flex items-center justify-between text-sm mb-2">
                            <span className="text-gray-700 font-medium">AI Confidence Score</span>
                            <span className={`font-bold ${config.textColor}`}>{confidencePercentage}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div
                                className={`bg-${config.color}-500 h-2.5 rounded-full transition-all duration-1000`}
                                style={{ width: `${confidencePercentage}%` }}
                            ></div>
                        </div>
                    </div>

                    {/* Fraud Indicators */}
                    {fraud_indicators && fraud_indicators.length > 0 && (
                        <div className="mt-4">
                            <h4 className={`text-sm font-bold ${config.textColor} mb-2`}>
                                Detected Issues ({fraud_indicators.length})
                            </h4>
                            <ul className="space-y-2">
                                {fraud_indicators.map((indicator, index) => (
                                    <li
                                        key={index}
                                        className="flex items-start gap-2 bg-white rounded-lg p-3 border border-gray-200"
                                    >
                                        <svg
                                            className={`w-5 h-5 ${config.textColor} flex-shrink-0 mt-0.5`}
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                            />
                                        </svg>
                                        <span className="text-sm text-gray-800">{indicator}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* No Issues Found */}
                    {(!fraud_indicators || fraud_indicators.length === 0) && !suspicious && (
                        <div className="mt-4 bg-white rounded-lg p-4 border border-success-200">
                            <div className="flex items-center gap-2">
                                <svg
                                    className="w-5 h-5 text-success-600"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                    />
                                </svg>
                                <span className="text-sm font-medium text-success-800">
                                    No fraud indicators detected. Receipt appears authentic.
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Recommendation */}
                    <div className="mt-4 pt-4 border-t border-gray-200">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-gray-700">Recommendation:</span>
                            <span className={`px-3 py-1 rounded-full badge-${config.color} text-sm font-bold`}>
                                {recommendation === 'REJECT' ? 'Reject Claim' :
                                    recommendation === 'MANUAL_REVIEW' ? 'Manual Review Required' :
                                        'Approve Claim'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FraudDetectionCard;
