import { useState } from 'react';
import { FaCheckCircle, FaExclamationTriangle, FaLightbulb, FaChevronDown, FaChevronUp } from 'react-icons/fa';
import type { ModuleInfo, MissingModuleInfo, AlternativeModule } from '../types';

interface ModuleAvailabilityProps {
  availableModules: ModuleInfo[];
  missingModules: MissingModuleInfo[];
  suggestedAlternatives: Array<{
    missing_module: string;
    alternatives: AlternativeModule[];
  }>;
  matchQuality: number;
}

export function ModuleAvailability({
  availableModules,
  missingModules,
  suggestedAlternatives,
  matchQuality,
}: ModuleAvailabilityProps) {
  const [showAvailable, setShowAvailable] = useState(false);
  const getMatchQualityColor = (quality: number) => {
    if (quality >= 0.8) return 'text-green-600';
    if (quality >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getMatchQualityBg = (quality: number) => {
    if (quality >= 0.8) return 'bg-green-100';
    if (quality >= 0.5) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      {/* Match Quality Indicator */}
      <div className={`${getMatchQualityBg(matchQuality)} rounded-lg p-4`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">Match Quality</h3>
            <p className="text-sm text-gray-600 mt-1">
              Based on your uploaded manuals
            </p>
          </div>
          <div className={`text-3xl font-bold ${getMatchQualityColor(matchQuality)}`}>
            {Math.round(matchQuality * 100)}%
          </div>
        </div>
      </div>

      {/* Available Modules */}
      {availableModules.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <button
            onClick={() => setShowAvailable(!showAvailable)}
            className="w-full flex items-center justify-between text-left hover:bg-gray-50 -m-6 p-6 rounded-lg transition-colors"
          >
            <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <FaCheckCircle className="text-green-600" />
              Available Modules ({availableModules.length})
            </h3>
            {showAvailable ? (
              <FaChevronUp className="text-gray-400" />
            ) : (
              <FaChevronDown className="text-gray-400" />
            )}
          </button>
          {showAvailable && (
            <div className="space-y-3 mt-4">
            {availableModules.map((module, index) => (
              <div
                key={index}
                className="border-l-4 border-green-500 pl-4 py-2 bg-green-50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">
                      {module.type.toUpperCase()}: {module.name}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {module.manufacturer} {module.model}
                    </div>
                    {module.features.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {module.features.slice(0, 3).map((feature, i) => (
                          <span
                            key={i}
                            className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="text-sm text-green-700 font-medium ml-4">
                    {Math.round(module.confidence * 100)}%
                  </div>
                </div>
              </div>
            ))}
            </div>
          )}
        </div>
      )}

      {/* Missing Modules */}
      {missingModules.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
            <FaExclamationTriangle className="text-yellow-600" />
            Missing Modules ({missingModules.length})
          </h3>
          <div className="space-y-3">
            {missingModules.map((module, index) => (
              <div key={index} className="border-l-4 border-yellow-500 pl-4 py-2 bg-yellow-50">
                <div className="font-medium text-gray-900">
                  {module.type.toUpperCase()}
                  {module.optional && (
                    <span className="ml-2 text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded">
                      Optional
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-600 mt-1">{module.role}</div>
                {module.specifications.length > 0 && (
                  <div className="text-xs text-gray-500 mt-2">
                    Required specs: {module.specifications.join(', ')}
                  </div>
                )}

                {/* Show alternatives if available */}
                {suggestedAlternatives.find((alt) => alt.missing_module === module.type) && (
                  <div className="mt-3 bg-white rounded p-3 border border-yellow-300">
                    <div className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                      <FaLightbulb className="text-yellow-600" />
                      Possible Alternatives:
                    </div>
                    <ul className="space-y-1 text-sm">
                      {suggestedAlternatives
                        .find((alt) => alt.missing_module === module.type)
                        ?.alternatives.map((alt, i) => (
                          <li key={i} className="text-gray-600">
                            • <span className="font-medium">{alt.type}:</span> {alt.note}
                          </li>
                        ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
