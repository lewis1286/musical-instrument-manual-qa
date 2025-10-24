import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  diagram: string;
  title?: string;
}

// Initialize mermaid with configuration
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'ui-sans-serif, system-ui, sans-serif',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis',
  },
});

export function MermaidDiagram({ diagram, title }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [svgCode, setSvgCode] = useState<string>('');

  useEffect(() => {
    const renderDiagram = async () => {
      if (!diagram || !containerRef.current) return;

      try {
        setError(null);

        // Generate unique ID for this diagram
        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

        // Render the diagram
        const { svg } = await mermaid.render(id, diagram);
        setSvgCode(svg);
      } catch (err: any) {
        console.error('Mermaid rendering error:', err);
        setError(err.message || 'Failed to render diagram');
      }
    };

    renderDiagram();
  }, [diagram]);

  if (!diagram) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {title && <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>}
      <div className="overflow-x-auto">
        {error ? (
          <div className="space-y-3">
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
              Unable to render diagram. Showing text representation:
            </div>
            <pre className="text-sm text-gray-700 bg-gray-50 p-4 rounded overflow-x-auto whitespace-pre-wrap">
              {diagram}
            </pre>
          </div>
        ) : (
          <div
            ref={containerRef}
            className="flex justify-center"
            dangerouslySetInnerHTML={{ __html: svgCode }}
          />
        )}
      </div>
    </div>
  );
}
