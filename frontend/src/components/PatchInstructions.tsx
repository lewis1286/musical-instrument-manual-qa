import { FaCheckCircle, FaBook } from 'react-icons/fa';
import type { PatchInstruction } from '../types';

interface PatchInstructionsProps {
  instructions: PatchInstruction[];
  parameterSuggestions?: Record<string, string>;
}

export function PatchInstructions({ instructions, parameterSuggestions }: PatchInstructionsProps) {
  if (!instructions || instructions.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
        <FaBook className="text-blue-600" />
        Patching Instructions
      </h3>

      <div className="space-y-4">
        {instructions.map((instruction) => (
          <div
            key={instruction.step}
            className="border-l-4 border-blue-500 pl-4 py-2 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-700 font-semibold">
                {instruction.step}
              </div>
              <div className="flex-1">
                <div className="font-medium text-gray-900 mb-1">
                  {instruction.module}
                </div>
                <div className="text-gray-700 mb-2">
                  {instruction.action}
                </div>

                {instruction.manual_reference && (
                  <div className="text-sm text-blue-600 italic flex items-center gap-1">
                    <FaBook className="text-xs" />
                    See {instruction.manual_reference}
                  </div>
                )}

                {instruction.settings && Object.keys(instruction.settings).length > 0 && (
                  <div className="mt-2 bg-gray-50 rounded p-2 text-sm">
                    <div className="font-medium text-gray-700 mb-1">Settings:</div>
                    <ul className="space-y-1">
                      {Object.entries(instruction.settings).map(([key, value]) => (
                        <li key={key} className="text-gray-600">
                          • <span className="font-medium">{key}:</span> {value}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {parameterSuggestions && Object.keys(parameterSuggestions).length > 0 && (
        <div className="mt-6 border-t pt-4">
          <h4 className="font-semibold text-gray-800 mb-3">Suggested Parameters</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(parameterSuggestions).map(([param, value]) => (
              <div key={param} className="bg-blue-50 rounded p-3">
                <div className="font-medium text-gray-800 text-sm">{param}</div>
                <div className="text-blue-700 text-sm mt-1">{value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
