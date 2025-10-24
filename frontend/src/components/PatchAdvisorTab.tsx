import { useState } from 'react';
import { FaRocket, FaLightbulb, FaSpinner } from 'react-icons/fa';
import { usePatchAdvisor } from '../hooks/usePatchAdvisor';
import { MermaidDiagram } from './MermaidDiagram';
import { PatchInstructions } from './PatchInstructions';
import { ModuleAvailability } from './ModuleAvailability';

export function PatchAdvisorTab() {
  const [query, setQuery] = useState('');
  const { patchDesign, loading, error, designPatch, clearPatch } = usePatchAdvisor();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      await designPatch(query);
    } catch (err) {
      // Error is handled by the hook
      console.error('Failed to design patch:', err);
    }
  };

  const exampleQueries = [
    'I want to create a dark, evolving drone sound',
    'I need a fat bass sound for techno',
    'How do I make a plucked string sound?',
    'I want to create an ambient pad',
    'How do I make a bell-like FM tone?',
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-3">
          <FaRocket className="text-3xl" />
          Patch Advisor
        </h2>
        <p className="text-purple-100">
          Describe the sound you want to create, and I'll design a modular patch using your equipment
        </p>
      </div>

      {/* Query Input */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit}>
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
            What sound do you want to create?
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., I want to create a dark, evolving drone sound..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-medium"
            >
              {loading ? (
                <>
                  <FaSpinner className="animate-spin" />
                  Designing...
                </>
              ) : (
                <>
                  <FaRocket />
                  Design Patch
                </>
              )}
            </button>
          </div>
        </form>

        {/* Example Queries */}
        {!patchDesign && !loading && (
          <div className="mt-4">
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
              <FaLightbulb className="text-yellow-500" />
              <span className="font-medium">Try these examples:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(example)}
                  className="text-sm px-3 py-2 bg-gray-100 hover:bg-purple-100 text-gray-700 hover:text-purple-700 rounded-lg transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FaSpinner className="animate-spin text-4xl text-purple-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Designing Your Patch</h3>
          <p className="text-gray-600">
            Analyzing sound requirements, matching modules, and creating instructions...
          </p>
        </div>
      )}

      {/* Patch Design Results */}
      {patchDesign && !loading && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {patchDesign.sound_type && patchDesign.sound_type.charAt(0).toUpperCase() + patchDesign.sound_type.slice(1)} Patch
                </h3>
                {patchDesign.characteristics.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {patchDesign.characteristics.map((char, i) => (
                      <span
                        key={i}
                        className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded-full"
                      >
                        {char}
                      </span>
                    ))}
                  </div>
                )}
                {patchDesign.synthesis_approach && (
                  <p className="text-gray-700 mb-2">
                    <span className="font-medium">Approach:</span> {patchDesign.synthesis_approach}
                  </p>
                )}
                {patchDesign.patch_template && (
                  <p className="text-sm text-gray-600">
                    Using template: <span className="font-medium">{patchDesign.patch_template}</span>
                  </p>
                )}
              </div>
              <button
                onClick={clearPatch}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Clear & Start Over
              </button>
            </div>
          </div>

          {/* Module Availability */}
          <ModuleAvailability
            availableModules={patchDesign.available_modules}
            missingModules={patchDesign.missing_modules}
            suggestedAlternatives={patchDesign.suggested_alternatives}
            matchQuality={patchDesign.match_quality}
          />

          {/* Signal Flow Diagram */}
          {patchDesign.mermaid_diagram && (
            <MermaidDiagram
              diagram={patchDesign.mermaid_diagram}
              title="Signal Flow Diagram"
            />
          )}

          {/* Patching Instructions */}
          <PatchInstructions
            instructions={patchDesign.instructions}
            parameterSuggestions={patchDesign.parameter_suggestions}
          />

          {/* Agent Messages (Debug) */}
          {patchDesign.agent_messages.length > 0 && (
            <details className="bg-gray-50 rounded-lg p-4">
              <summary className="cursor-pointer text-sm font-medium text-gray-700">
                Agent Workflow Details
              </summary>
              <div className="mt-3 space-y-1">
                {patchDesign.agent_messages.map((msg, i) => (
                  <div key={i} className="text-sm text-gray-600">
                    {msg}
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}

      {/* Empty State */}
      {!patchDesign && !loading && !error && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FaRocket className="text-6xl text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Ready to Design Your Patch
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Describe the sound you want to create, and I'll analyze your uploaded manuals to design
            a modular patch with step-by-step instructions.
          </p>
        </div>
      )}
    </div>
  );
}
