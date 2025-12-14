import React, { useState, useEffect } from 'react';
import ClaimUpload from './components/ClaimUpload';
import AnalysisResults from './components/AnalysisResults';

// Backend API URL - uses environment variable or fallback to localhost
import ClaimHistory from './components/ClaimHistory';

// Backend API URL - uses environment variable or fallback to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(false);

  // 6-stage workflow stages
  const processingStages = [
    { id: 1, name: 'Uploading', icon: '📤', description: 'Uploading receipt to server' },
    { id: 2, name: 'Vision Analysis', icon: '👁️', description: 'Extracting data with AI Vision' },
    { id: 3, name: 'Fraud Detection', icon: '🔍', description: 'Analyzing for fraud indicators' },
    { id: 4, name: 'Policy Check', icon: '📋', description: 'Validating against policy rules' },
    { id: 5, name: 'Medical Review', icon: '⚕️', description: 'Checking medical necessity' },
    { id: 6, name: 'Finalizing', icon: '✅', description: 'Generating final decision' }
  ];

  // Check system health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/health`);
        setIsOnline(res.ok);
      } catch (e) {
        setIsOnline(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000); // Check every 5s
    return () => clearInterval(interval);
  }, []);

  const handleHistoryView = (fullData) => {
    const transformedData = transformBackendResponse(fullData);
    setAnalysisResult(transformedData);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleUpload = async (file) => {
    setIsProcessing(true);
    setProcessingStage(0);
    setAnalysisResult(null);
    setError(null);

    // Simulate stage progression for visual feedback
    const stageTimings = [0, 300, 1000, 1500, 2000, 2500]; // Delays for each stage

    try {
      // Create FormData to send file
      const formData = new FormData();
      formData.append('file', file);

      console.log('📤 Uploading file to backend:', file.name);

      // Stage 1: Uploading
      setProcessingStage(1);

      // Make API call to backend
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      // Stage 2: Vision Analysis (simulated)
      setTimeout(() => setProcessingStage(2), stageTimings[1]);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      // Stage 3: Fraud Detection
      setTimeout(() => setProcessingStage(3), stageTimings[2]);

      const data = await response.json();
      console.log('✅ Received response from backend:', data);

      // Stage 4: Policy Check
      setTimeout(() => setProcessingStage(4), stageTimings[3]);

      // Stage 5: Medical Review
      setTimeout(() => setProcessingStage(5), stageTimings[4]);

      // Stage 6: Finalizing
      setTimeout(() => setProcessingStage(6), stageTimings[5]);

      // Transform backend response to match AnalysisResults component expectations
      const transformedData = transformBackendResponse(data);

      // Small delay before showing results for smooth transition
      setTimeout(() => {
        setAnalysisResult(transformedData);
        setIsProcessing(false);
        setProcessingStage(0);
      }, 3000);

    } catch (err) {
      console.error('❌ Error analyzing claim:', err);
      setError(err.message || 'Failed to analyze claim. Please ensure the backend server is running.');
      setIsProcessing(false);
      setProcessingStage(0);

      // Show error to user
      alert(`Error: ${err.message}\n\nPlease ensure:\n1. Backend server is running (python backend/main.py)\n2. Server is accessible at ${API_URL}`);
    }
  };

  /**
   * Transform backend API response to match the format expected by AnalysisResults component
   */
  const transformBackendResponse = (backendData) => {
    console.log('🔍 DEBUG: Backend Response:', backendData);
    console.log('🔍 DEBUG: final_decision:', backendData.final_decision);

    // Edge case: Validate backend data structure
    if (!backendData || typeof backendData !== 'object') {
      console.error('❌ Invalid backend response:', backendData);
      throw new Error('Invalid response from backend');
    }

    const policyResult = backendData.policy_adjudication || {};
    const visionAnalysis = backendData.vision_analysis || {};

    // Edge case: Warn if critical data is missing
    if (!policyResult.line_item_decisions || policyResult.line_item_decisions.length === 0) {
      console.warn('⚠️ No line item decisions found in backend response');
    }

    // Map line_item_decisions to line_items format
    const lineItems = (policyResult.line_item_decisions || []).map(decision => {
      // CRITICAL FIX: Override approved_amount to 0 for contraindicated medications
      // Backend sets total_approved=0 but doesn't update individual line items

      // Edge case: Handle missing or invalid medical_severity
      const medicalSeverity = decision.medical_severity || null;
      const isContraindicated = medicalSeverity === 'CRITICAL';

      // Edge case: Handle missing approved_amount (fallback to claimed_amount)
      const claimedAmount = decision.claimed_amount || 0;
      const backendApprovedAmount = decision.approved_amount !== undefined ? decision.approved_amount : claimedAmount;
      const approvedAmount = isContraindicated ? 0 : backendApprovedAmount;

      return {
        name: decision.item_name || 'Unknown Item',
        quantity: decision.quantity || 1,
        total_price: claimedAmount,
        approved_amount: approvedAmount, // Use overridden amount for contraindicated items
        category: decision.category || '',
        status: decision.status || 'UNKNOWN',
        excluded: decision.status === 'REJECTED',
        exclusion_reason: decision.status === 'REJECTED' ? (decision.reason || 'No reason provided') : null,
        medical_necessity: decision.medical_necessity || null,
        medical_reason: decision.medical_reason || null,
        medical_severity: medicalSeverity // Map severity level with null safety
      };
    });

    // Extract excluded items for the summary section
    const excludedItems = (policyResult.line_item_decisions || [])
      .filter(decision => decision.status === 'REJECTED')
      .map(decision => ({
        item_name: decision.item_name,
        amount: decision.claimed_amount,
        reason: decision.reason
      }));


    return {
      claim_id: policyResult.claim_id || 'N/A',
      claim_type: policyResult.claim_type || 'N/A',
      merchant_name: policyResult.merchant_name || visionAnalysis.merchant_name || 'N/A',
      merchant_address: visionAnalysis.merchant_address || 'N/A',
      date: visionAnalysis.date || 'N/A',
      patient_name: policyResult.patient_name || 'N/A',
      status: backendData.final_decision?.status || policyResult.status || 'UNKNOWN',  // Use final_decision status (with overrides)
      line_items: lineItems,
      total_amount: policyResult.total_claimed || 0,
      subtotal: policyResult.total_claimed || 0,
      excluded_items_found: excludedItems,
      excluded_amount: backendData.final_decision?.total_deducted || policyResult.total_deducted || 0,  // Use final_decision (with overrides)
      approved_amount: backendData.final_decision?.total_approved || policyResult.total_approved || 0,  // Use final_decision (with overrides)
      reason: backendData.final_decision?.summary || policyResult.summary || 'Analysis complete',  // Use final_decision summary
      fraud_detection: visionAnalysis.fraud_detection || null,  // Add fraud detection data
      diagnosis_or_specialty: visionAnalysis.diagnosis_or_specialty || null  // Add diagnosis for display
    };
  };

  const handleReset = () => {
    setAnalysisResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ClaimGuard AI</h1>
                <p className="text-sm text-gray-600">Forensic Adjudication Engine</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600">
                <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-success-500 animate-pulse' : 'bg-danger-500'}`}></span>
                {isOnline ? 'System Online' : 'System Offline'}
              </div>
              <div className="px-4 py-2 bg-primary-100 text-primary-700 rounded-lg text-sm font-medium">
                Assemble Hack 2025
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!analysisResult ? (
          <>
            {/* Hero Section */}
            <div className="text-center mb-12 animate-fade-in">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Automated Insurance Claim Adjudication
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Powered by AI Vision and intelligent policy enforcement.
                Detect fraud, validate exclusions, and process claims in seconds.
              </p>
              <div className="mt-6 flex items-center justify-center gap-6 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>Instant Processing</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>85+ Exclusions</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>Fraud Detection</span>
                </div>
              </div>
            </div>

            {/* Upload Component */}
            <ClaimUpload onUpload={handleUpload} isProcessing={isProcessing} />

            {/* 6-Stage Progress Indicator */}
            {isProcessing && (
              <div className="mt-8 max-w-4xl mx-auto bounce-in">
                <div className="card glass border-primary-200">
                  <div className="text-center mb-6">
                    <h3 className="text-2xl font-bold gradient-text mb-2">Processing Your Claim</h3>
                    <p className="text-gray-600">AI-powered analysis in progress...</p>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-8">
                    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${(processingStage / 6) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Stage Cards */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {processingStages.map((stage) => {
                      const isActive = processingStage === stage.id;
                      const isCompleted = processingStage > stage.id;
                      const isPending = processingStage < stage.id;

                      return (
                        <div
                          key={stage.id}
                          className={`p-4 rounded-lg border-2 transition-all duration-300 ${isActive
                              ? 'border-primary-500 bg-primary-50 shadow-lg scale-105 pulse-glow-primary'
                              : isCompleted
                                ? 'border-success-400 bg-success-50'
                                : 'border-gray-200 bg-gray-50 opacity-60'
                            }`}
                        >
                          <div className="flex items-center gap-3 mb-2">
                            <div
                              className={`text-3xl ${isActive ? 'animate-bounce' : isCompleted ? '' : 'grayscale'
                                }`}
                            >
                              {stage.icon}
                            </div>
                            <div className="flex-1">
                              <h4
                                className={`font-bold text-sm ${isActive
                                    ? 'text-primary-700'
                                    : isCompleted
                                      ? 'text-success-700'
                                      : 'text-gray-500'
                                  }`}
                              >
                                {stage.name}
                              </h4>
                            </div>
                            {isCompleted && (
                              <svg
                                className="w-5 h-5 text-success-600 animate-bounce-in"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M5 13l4 4L19 7"
                                />
                              </svg>
                            )}
                            {isActive && (
                              <div className="animate-spin">
                                <svg
                                  className="w-5 h-5 text-primary-600"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                >
                                  <circle
                                    className="opacity-25"
                                    cx="12"
                                    cy="12"
                                    r="10"
                                    stroke="currentColor"
                                    strokeWidth="4"
                                  ></circle>
                                  <path
                                    className="opacity-75"
                                    fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                  ></path>
                                </svg>
                              </div>
                            )}
                          </div>
                          <p
                            className={`text-xs ${isActive ? 'text-primary-600' : isCompleted ? 'text-success-600' : 'text-gray-400'
                              }`}
                          >
                            {stage.description}
                          </p>
                        </div>
                      );
                    })}
                  </div>

                  {/* Current Stage Message */}
                  {processingStage > 0 && processingStage <= 6 && (
                    <div className="mt-6 text-center animate-fade-in">
                      <p className="text-sm text-gray-600">
                        <span className="font-semibold text-primary-700">
                          {processingStages[processingStage - 1].name}
                        </span>
                        {' • '}
                        {processingStages[processingStage - 1].description}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* History Component - Only shown on home screen */}
            <ClaimHistory onViewClaim={handleHistoryView} />
          </>
        ) : (
          <>
            {/* Results */}
            <AnalysisResults result={analysisResult} />

            {/* Actions */}
            <div className="mt-8 flex justify-center gap-4 animate-fade-in">
              <button
                onClick={handleReset}
                className="btn-primary"
              >
                <svg className="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Process Another Claim
              </button>
              <button className="btn-secondary">
                <svg className="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Report
              </button>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold text-gray-900 mb-2">ClaimGuard AI</h3>
              <p className="text-sm text-gray-600">
                Automated forensic adjudication for Indian health insurance claims.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-2">Features</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• AI-powered fraud detection</li>
                <li>• Room rent capping automation</li>
                <li>• Policy exclusion validation</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-2">Built with</h3>
              <p className="text-sm text-gray-600">
                React • Tailwind CSS • Python • Kestra<br />
                Cline • Vertex AI
              </p>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-200 text-center text-sm text-gray-600">
            <p>Built for Assemble Hack 2025 • © 2025 ClaimGuard AI</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
