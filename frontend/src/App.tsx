import { useState, useRef } from 'react';
import { FaUpload, FaTrash, FaBook, FaChartBar, FaRedo } from 'react-icons/fa';
import { useManuals } from './hooks/useManuals';
import { useQA } from './hooks/useQA';
import { useStats } from './hooks/useStats';
import type { ManualSaveRequest } from './types';

function App() {
  const { manuals, pendingManual, loading: manualsLoading, error: manualsError, processManual, saveManual, cancelUpload, deleteManual } = useManuals();
  const { answer, sources, loading: qaLoading, error: qaError, askQuestion, clearHistory } = useQA();
  const { stats, loading: statsLoading, manufacturers, instrumentTypes, resetDatabase } = useStats();

  const [question, setQuestion] = useState('');
  const [activeTab, setActiveTab] = useState<'qa' | 'manuals' | 'stats'>('qa');
  const [editMetadata, setEditMetadata] = useState({
    display_name: '',
    manufacturer: '',
    model: '',
    instrument_type: '',
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const pending = await processManual(file);
      setEditMetadata({
        display_name: pending.metadata.display_name,
        manufacturer: pending.metadata.manufacturer || '',
        model: pending.metadata.model || '',
        instrument_type: pending.metadata.instrument_type || '',
      });
    } catch (err) {
      console.error('Upload failed:', err);
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle save manual
  const handleSaveManual = async () => {
    if (!pendingManual) return;

    const request: ManualSaveRequest = {
      filename: pendingManual.original_filename,
      display_name: editMetadata.display_name,
      manufacturer: editMetadata.manufacturer,
      model: editMetadata.model,
      instrument_type: editMetadata.instrument_type,
    };

    try {
      await saveManual(request);
    } catch (err) {
      console.error('Save failed:', err);
    }
  };

  // Handle ask question
  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    await askQuestion({ question });
  };

  // Handle reset database
  const handleResetDatabase = async () => {
    if (window.confirm('Are you sure you want to reset the database? This will delete all manuals and cannot be undone!')) {
      await resetDatabase();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <FaBook className="text-4xl" />
            Musical Instrument Manual Q&A
          </h1>
          <p className="text-blue-100 mt-2">Ask questions about your instrument manuals using AI</p>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('qa')}
              className={`px-6 py-4 font-semibold border-b-2 transition-colors ${
                activeTab === 'qa'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-blue-600'
              }`}
            >
              Ask Questions
            </button>
            <button
              onClick={() => setActiveTab('manuals')}
              className={`px-6 py-4 font-semibold border-b-2 transition-colors ${
                activeTab === 'manuals'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-blue-600'
              }`}
            >
              Manage Manuals ({manuals.length})
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`px-6 py-4 font-semibold border-b-2 transition-colors ${
                activeTab === 'stats'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-blue-600'
              }`}
            >
              <FaChartBar className="inline mr-2" />
              Statistics
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Q&A Tab */}
        {activeTab === 'qa' && (
          <div className="max-w-4xl mx-auto">
            {/* Question Form */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <form onSubmit={handleAskQuestion}>
                <label className="block text-lg font-semibold mb-3 text-gray-700">
                  Ask a question about your instruments:
                </label>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={3}
                  placeholder="e.g., How do I connect my synthesizer via MIDI?"
                  disabled={qaLoading}
                />
                <div className="mt-4 flex gap-3">
                  <button
                    type="submit"
                    disabled={qaLoading || !question.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold transition-colors"
                  >
                    {qaLoading ? 'Searching...' : 'Ask Question'}
                  </button>
                  <button
                    type="button"
                    onClick={clearHistory}
                    className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-semibold transition-colors"
                  >
                    Clear History
                  </button>
                </div>
              </form>

              {qaError && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  {qaError}
                </div>
              )}
            </div>

            {/* Answer Display */}
            {answer && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-800">Answer:</h2>
                <div className="prose max-w-none mb-6">
                  <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{answer}</p>
                </div>

                {/* Sources */}
                {sources.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-lg font-semibold mb-3 text-gray-800">Sources:</h3>
                    <div className="space-y-3">
                      {sources.map((source, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <span className="font-semibold text-blue-600">{source.display_name}</span>
                              <span className="text-gray-600 ml-2">• Page {source.page_number}</span>
                            </div>
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {source.section_type}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600">
                            {source.manufacturer} • {source.model} • {source.instrument_type}
                          </div>
                          <p className="text-sm text-gray-700 mt-2 italic">{source.content_preview}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!answer && !qaLoading && (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <FaBook className="text-6xl text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">Ask a question to get started!</p>
                <p className="text-gray-400 mt-2">Upload manuals in the "Manage Manuals" tab first.</p>
              </div>
            )}
          </div>
        )}

        {/* Manuals Tab */}
        {activeTab === 'manuals' && (
          <div className="max-w-6xl mx-auto">
            {/* Upload Section */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-bold mb-4 text-gray-800">Upload Manual</h2>
              <div className="flex gap-4 items-center">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="fileInput"
                  disabled={manualsLoading}
                />
                <label
                  htmlFor="fileInput"
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer font-semibold flex items-center gap-2 transition-colors"
                >
                  <FaUpload /> Upload PDF Manual
                </label>
                {manualsLoading && <span className="text-gray-600">Processing...</span>}
              </div>

              {manualsError && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  {manualsError}
                </div>
              )}
            </div>

            {/* Pending Manual Edit */}
            {pendingManual && (
              <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg shadow-md p-6 mb-6">
                <h3 className="text-lg font-bold mb-4 text-gray-800">Review and Edit Metadata</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-semibold mb-1 text-gray-700">Display Name</label>
                    <input
                      type="text"
                      value={editMetadata.display_name}
                      onChange={(e) => setEditMetadata({ ...editMetadata, display_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-1 text-gray-700">Manufacturer</label>
                    <input
                      type="text"
                      value={editMetadata.manufacturer}
                      onChange={(e) => setEditMetadata({ ...editMetadata, manufacturer: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Moog, Roland, Korg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-1 text-gray-700">Model</label>
                    <input
                      type="text"
                      value={editMetadata.model}
                      onChange={(e) => setEditMetadata({ ...editMetadata, model: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Minimoog, Jupiter-8"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-1 text-gray-700">Instrument Type</label>
                    <input
                      type="text"
                      value={editMetadata.instrument_type}
                      onChange={(e) => setEditMetadata({ ...editMetadata, instrument_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Synthesizer, Mixer"
                    />
                  </div>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleSaveManual}
                    disabled={manualsLoading}
                    className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 font-semibold transition-colors"
                  >
                    Save Manual
                  </button>
                  <button
                    onClick={cancelUpload}
                    disabled={manualsLoading}
                    className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 font-semibold transition-colors"
                  >
                    Cancel
                  </button>
                </div>
                <p className="text-sm text-gray-600 mt-3">
                  Total Pages: {pendingManual.metadata.total_pages} • Chunks: {pendingManual.chunk_count}
                </p>
              </div>
            )}

            {/* Manuals List */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-800">Uploaded Manuals</h2>
              {manuals.length === 0 ? (
                <div className="text-center py-12">
                  <FaBook className="text-6xl text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">No manuals uploaded yet</p>
                  <p className="text-gray-400 mt-2">Upload a PDF manual to get started</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {manuals.map((manual) => (
                    <div key={manual.filename} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-800">{manual.display_name}</h3>
                          <div className="text-sm text-gray-600 mt-1">
                            <span>{manual.manufacturer}</span> • <span>{manual.model}</span> • <span>{manual.instrument_type}</span>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {manual.total_pages} pages • {manual.chunk_count} chunks
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            if (window.confirm(`Are you sure you want to delete "${manual.display_name}"? This cannot be undone.`)) {
                              deleteManual(manual.filename);
                            }
                          }}
                          className="px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 flex items-center gap-2 transition-colors"
                        >
                          <FaTrash /> Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Stats Tab */}
        {activeTab === 'stats' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-800">Database Statistics</h2>
                <button
                  onClick={handleResetDatabase}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 font-semibold transition-colors"
                >
                  <FaRedo /> Reset Database
                </button>
              </div>

              {statsLoading ? (
                <p className="text-gray-500">Loading statistics...</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h3 className="text-sm font-semibold text-gray-600 mb-2">Total Manuals</h3>
                    <p className="text-3xl font-bold text-blue-600">{stats.total_manuals}</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h3 className="text-sm font-semibold text-gray-600 mb-2">Total Chunks</h3>
                    <p className="text-3xl font-bold text-green-600">{stats.total_chunks}</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h3 className="text-sm font-semibold text-gray-600 mb-2">Manufacturers</h3>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {manufacturers.length > 0 ? (
                        manufacturers.map((m) => (
                          <span key={m} className="px-2 py-1 bg-purple-200 text-purple-800 text-xs rounded">
                            {m}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-400 text-sm">None</span>
                      )}
                    </div>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h3 className="text-sm font-semibold text-gray-600 mb-2">Instrument Types</h3>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {instrumentTypes.length > 0 ? (
                        instrumentTypes.map((t) => (
                          <span key={t} className="px-2 py-1 bg-orange-200 text-orange-800 text-xs rounded">
                            {t}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-400 text-sm">None</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 mt-12">
        <div className="container mx-auto px-4 py-6 text-center">
          <p>Musical Instrument Manual Q&A System • Powered by OpenAI & ChromaDB</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
