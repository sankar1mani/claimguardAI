import React, { useState } from 'react';
import ClaimUpload from './components/ClaimUpload';
import AnalysisResults from './components/AnalysisResults';

// Backend API URL - uses environment variable or fallback to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setIsProcessing(true);
    setAnalysisResult(null);
    setError(null);

    try {
      // Create FormData to send file
      const formData = new FormData();
      formData.append('file', file);

      console.log('📤 Uploading file to backend:', file.name);

      // Make API call to backend
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Received response from backend:', data);

      // Transform backend response to match AnalysisResults component expectations
      const transformedData = transformBackendResponse(data);
      setAnalysisResult(transformedData);

    } catch (err) {
      console.error('❌ Error analyzing claim:', err);
      setError(err.message || 'Failed to analyze claim. Please ensure the backend server is running.');

      // Show error to user
      alert(`Error: ${err.message}\n\nPlease ensure:\n1. Backend server is running (python backend/main.py)\n2. Server is accessible at ${API_URL}`);
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * Transform backend API response to match the format expected by AnalysisResults component
   */
  const transformBackendResponse = (backendData) => {
    const policyResult = backendData.policy_adjudication || {};
    const visionAnalysis = backendData.vision_analysis || {};

    // Map line_item_decisions to line_items format
    const lineItems = (policyResult.line_item_decisions || []).map(decision => ({
      name: decision.item_name,
      quantity: 1, // Backend doesn't return quantity in decisions
      total_price: decision.claimed_amount,
      category: '', // Backend doesn't return category in decisions
      status: decision.status,
      excluded: decision.status === 'REJECTED',
      exclusion_reason: decision.status === 'REJECTED' ? decision.reason : null
    }));

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
      status: policyResult.status || 'UNKNOWN',
      line_items: lineItems,
      total_amount: policyResult.total_claimed || 0,
      subtotal: policyResult.total_claimed || 0,
      excluded_items_found: excludedItems,
      excluded_amount: policyResult.total_deducted || 0,
      approved_amount: policyResult.total_approved || 0,
      reason: policyResult.summary || backendData.final_decision?.summary || 'Analysis complete'
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
                <span className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></span>
                System Online
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
                Google Gemini • Together AI
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
