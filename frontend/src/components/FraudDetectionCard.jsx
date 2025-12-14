import React, { useEffect, useState } from 'react';

const FraudDetectionCard = ({ fraudDetection }) => {
    const [shouldShake, setShouldShake] = useState(false);

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

    // Trigger shake animation for HIGH risk on mount
    useEffect(() => {
        if (riskLevel === 'HIGH') {
            setShouldShake(true);
            const timer = setTimeout(() => setShouldShake(false), 500);
            return () => clearTimeout(timer);
        }
    }, [riskLevel]);

    // Risk level configurations with enhanced styling
    const riskConfig = {
        HIGH: {
            color: 'danger',
            bgColor: 'bg-gradient-to-br from-danger-50 via-danger-100 to-danger-50',
            borderColor: 'border-danger-400',
            textColor: 'text-danger-900',
            iconBg: 'bg-gradient-to-br from-danger-500 to-danger-700',
            icon: '🚨',
            label: 'High Risk',
            description: 'Significant fraud indicators detected',
            glowClass: 'pulse-glow-danger'
        },
        MEDIUM: {
            color: 'warning',
            bgColor: 'bg-gradient-to-br from-warning-50 via-warning-100 to-warning-50',
            borderColor: 'border-warning-400',
            textColor: 'text-warning-900',
            iconBg: 'bg-gradient-to-br from-warning-500 to-warning-700',
            icon: '⚠️',
            label: 'Medium Risk',
            description: 'Manual review recommended',
            glowClass: 'pulse-glow-warning'
        },
        LOW: {
            color: 'success',
            bgColor: 'bg-gradient-to-br from-success-50 via-success-100 to-success-50',
            borderColor: 'border-success-400',
            textColor: 'text-success-900',
            iconBg: 'bg-gradient-to-br from-success-500 to-success-700',
            icon: '✅',
            label: 'Low Risk',
            description: 'No significant fraud indicators',
            glowClass: 'pulse-glow-success'
        }
    };

    const config = riskConfig[riskLevel];
    const confidencePercentage = (confidence_score * 100).toFixed(1);

    return (
        <div className={`card ${config.bgColor} ${config.borderColor} border-2 ${riskLevel === 'HIGH' ? config.glowClass : ''} ${shouldShake ? 'shake' : ''} bounce-in`}>
            <div className="flex items-start gap-4">
                {/* Icon with animation */}
                <div className="flex-shrink-0">
                    <div className={`w-20 h-20 rounded-full ${config.iconBg} flex items-center justify-center text-4xl border-2 ${config.borderColor} shadow-lg ${riskLevel === 'HIGH' ? 'animate-pulse' : 'float'}`}>
                        {config.icon}
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1">
                    <div className="flex items-center justify-between mb-3">
                        <div>
                            <h3 className={`text-2xl font-bold ${config.textColor} mb-1`}>
                                Fraud Detection Analysis
                            </h3>
                            <p className="text-sm text-gray-600">{config.description}</p>
                        </div>
                        <div className={`px-5 py-2.5 rounded-full badge-${config.color} font-bold text-base shadow-md`}>
                            {config.label}
                        </div>
                    </div>

                    {/* Confidence Score with animated progress bar */}
                    <div className="mb-4">
                        <div className="flex items-center justify-between text-sm mb-2">
                            <span className="text-gray-700 font-medium">AI Confidence Score</span>
                            <span className={`font-bold ${config.textColor} text-lg`}>{confidencePercentage}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
                            <div
                                className={`bg-gradient-to-r from-${config.color}-500 to-${config.color}-600 h-3 rounded-full transition-all duration-1000 ease-out`}
                                style={{
                                    width: `${confidencePercentage}%`,
                                    animation: 'progress-bar 1.5s ease-out'
                                }}
                            ></div>
                        </div>
                    </div>

                    {/* Fraud Indicators with staggered animation */}
                    {fraud_indicators && fraud_indicators.length > 0 && (
                        <div className="mt-4">
                            <h4 className={`text-sm font-bold ${config.textColor} mb-3 flex items-center gap-2`}>
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                                Detected Issues ({fraud_indicators.length})
                            </h4>
                            <ul className="space-y-2">
                                {fraud_indicators.map((indicator, index) => (
                                    <li
                                        key={index}
                                        className={`stagger-item flex items-start gap-2 bg-white rounded-lg p-3 border-l-4 border-${config.color}-500 shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-0.5`}
                                    >
                                        <svg
                                            className={`w-5 h-5 ${config.textColor} flex-shrink-0 mt-0.5 ${riskLevel === 'HIGH' ? 'animate-pulse' : ''}`}
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
                                        <span className="text-sm text-gray-800 font-medium">{indicator}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* No Issues Found */}
                    {(!fraud_indicators || fraud_indicators.length === 0) && !suspicious && (
                        <div className="mt-4 bg-white rounded-lg p-4 border-l-4 border-success-500 shadow-sm bounce-in">
                            <div className="flex items-center gap-2">
                                <svg
                                    className="w-6 h-6 text-success-600"
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

                    {/* Recommendation with enhanced styling */}
                    <div className="mt-5 pt-4 border-t-2 border-gray-200">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-bold text-gray-700 flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                                </svg>
                                Recommendation:
                            </span>
                            <span className={`px-4 py-2 rounded-full badge-${config.color} text-sm font-bold shadow-md ${riskLevel === 'HIGH' ? 'animate-pulse' : ''}`}>
                                {recommendation === 'REJECT' ? '🚫 Reject Claim' :
                                    recommendation === 'MANUAL_REVIEW' ? '👁️ Manual Review Required' :
                                        '✅ Approve Claim'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FraudDetectionCard;

