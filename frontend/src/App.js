import React, { useState } from 'react';

const STAGES = [
  { id: 'tokens', label: '1. Tokens' },
  { id: 'ast', label: '2. AST' },
  { id: 'semantic', label: '3. Semantic' },
  { id: 'ir', label: '4. Raw IR' },
  { id: 'optimized_ir', label: '5. Optimized IR' },
  { id: 'cfg', label: '6. CFG' },
  { id: 'registers', label: '7. Registers' },
  { id: 'vm', label: '8. VM Output' },
  { id: 'c_code', label: '9. C Transpiler' },
];

function App() {
  const [code, setCode] = useState(`// Global variables
int a = 5;
int b = 10;
string message = "Starting calculation";

// Function definition
func multiply(int x, int y) int {
    return x * y;
}

// Data redundancy (Constant Folding + Propagation + CSE)
int c = a + 2 * 3;
int d = a + 2 * 3; // CSE should catch this!

// Function call
int result = multiply(c, d);

// While loop and Logical Operators
bool flag = true;
int counter = 0;

while (counter < 5 && flag == true) {
    print(message);
    counter = counter + 1;
    if (counter == 4) {
        flag = false; // Escaping the loop early
    }
}

print(result);`);

  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('vm');

  const handleCompile = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5001/compile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });
      
      const data = await response.json();
      if (data.success) {
        setOutput(data.stages);
        setActiveTab('vm'); // Auto switch to VM output on success
      } else {
        setError(data.error);
        setOutput(data.stages);
        // Switch to the first available tab, or show error
        setActiveTab(Object.keys(data.stages)[0] || 'tokens');
      }
    } catch (err) {
      setError('Failed to connect to the compiler backend. Make sure the Flask server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-white p-4 lg:p-8 font-sans selection:bg-blue-500/30">
      <div className="max-w-[1400px] mx-auto">
        
        {/* Header */}
        <header className="flex justify-between items-end mb-8 border-b border-gray-800 pb-4">
          <div>
            <h1 className="text-4xl lg:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">
              Nexus<span className="text-white">Compiler</span>
            </h1>
            <p className="text-gray-400 mt-2 text-sm lg:text-base font-medium">
              Interactive 9-Stage Compiler Pipeline
            </p>
          </div>
          <button 
            onClick={handleCompile}
            disabled={loading}
            className="group relative inline-flex items-center justify-center px-8 py-3 text-sm font-bold text-white transition-all duration-200 bg-blue-600 font-pj rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
          >
            <span className="relative z-10 flex items-center gap-2">
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Compiling...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                  Compile Code
                </>
              )}
            </span>
            <div className="absolute inset-0 h-full w-full bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-in-out"></div>
          </button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[75vh]">
          
          {/* Editor Panel */}
          <div className="flex flex-col bg-[#111827] rounded-2xl border border-gray-800 shadow-2xl overflow-hidden backdrop-blur-sm">
            <div className="bg-[#1F2937] px-4 py-3 border-b border-gray-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="ml-2 text-xs font-mono text-gray-400">source.nx</span>
              </div>
            </div>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="flex-grow w-full bg-transparent text-emerald-300 font-mono text-sm p-5 focus:outline-none resize-none leading-relaxed"
              spellCheck="false"
            />
            {error && (
              <div className="p-4 bg-red-900/40 border-t border-red-500/50 text-red-200 font-mono text-sm whitespace-pre-wrap">
                <span className="font-bold text-red-400 mr-2">Error:</span>
                {error}
              </div>
            )}
          </div>

          {/* Visualization Panel */}
          <div className="flex flex-col bg-[#111827] rounded-2xl border border-gray-800 shadow-2xl overflow-hidden backdrop-blur-sm relative">
            
            {/* Tabs */}
            <div className="flex overflow-x-auto bg-[#1F2937] border-b border-gray-800 scrollbar-hide">
              {STAGES.map((stage) => (
                <button
                  key={stage.id}
                  onClick={() => setActiveTab(stage.id)}
                  disabled={!output || !output[stage.id]}
                  className={`whitespace-nowrap px-5 py-3 text-xs font-mono font-semibold transition-all duration-200
                    ${activeTab === stage.id 
                      ? 'bg-[#111827] text-blue-400 border-t-2 border-blue-500' 
                      : 'text-gray-500 hover:bg-gray-800 hover:text-gray-300'}
                    ${(!output || !output[stage.id]) ? 'opacity-30 cursor-not-allowed' : ''}
                  `}
                >
                  {stage.label}
                </button>
              ))}
            </div>

            {/* Content Area */}
            <div className="flex-grow p-5 overflow-y-auto font-mono text-sm relative">
              {!output ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <p className="font-medium tracking-wide">AWAITING COMPILATION</p>
                  <p className="text-xs mt-2 opacity-50">Click compile to generate pipeline data</p>
                </div>
              ) : (
                <div className="h-full w-full">
                  {/* Content rendered dynamically based on active tab */}
                  {activeTab === 'vm' ? (
                    <div className="h-full flex flex-col">
                      <div className="bg-black/50 p-4 rounded-lg border border-gray-800 flex-grow overflow-auto shadow-inner">
                        <div className="text-xs text-gray-500 mb-2">// stdout</div>
                        <pre className="text-green-400 whitespace-pre-wrap">{output[activeTab]}</pre>
                      </div>
                    </div>
                  ) : activeTab === 'c_code' ? (
                    <div className="h-full">
                      <pre className="text-blue-300 whitespace-pre-wrap">{output[activeTab]}</pre>
                    </div>
                  ) : (
                    <div className="h-full">
                      <pre className="text-gray-300 whitespace-pre-wrap">{output[activeTab]}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
