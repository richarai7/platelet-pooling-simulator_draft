interface WhatIfGuideProps {
  onClose?: () => void;
}

export function WhatIfQuickReference({ onClose }: WhatIfGuideProps) {
  return (
    <div className="quick-reference-modal">
      <div className="quick-reference-content">
        <div className="quick-reference-header">
          <h2>What-If Analysis Quick Reference</h2>
          {onClose && (
            <button onClick={onClose} className="close-button">✖</button>
          )}
        </div>
        
        <div className="reference-grid">
          <div className="reference-card">
            <div className="card-icon">🧑‍🔬</div>
            <h3>1. Staff Allocation</h3>
            <p><strong>Test:</strong> Different staffing levels</p>
            <p><strong>How:</strong> Set device type="person", adjust capacity</p>
            <p><strong>Check:</strong> Staff utilization, bottleneck analysis</p>
            <p><strong>Goal:</strong> Red bars (&gt;85%) = need more staff</p>
          </div>

          <div className="reference-card">
            <div className="card-icon">🏭</div>
            <h3>2. Device Utilization</h3>
            <p><strong>Test:</strong> Equipment optimization</p>
            <p><strong>How:</strong> Adjust device capacities</p>
            <p><strong>Check:</strong> Utilization bars, bottleneck field</p>
            <p><strong>Goal:</strong> Balance utilization (60-85% ideal)</p>
          </div>

          <div className="reference-card">
            <div className="card-icon">📊</div>
            <h3>3. Supply Variation</h3>
            <p><strong>Test:</strong> Handle uncertainty</p>
            <p><strong>How:</strong> Set process_time_range [min, max]</p>
            <p><strong>Check:</strong> Supply variation metric</p>
            <p><strong>Goal:</strong> Test with different random seeds</p>
          </div>

          <div className="reference-card">
            <div className="card-icon">🔄</div>
            <h3>4. Process Order</h3>
            <p><strong>Test:</strong> Workflow sequences</p>
            <p><strong>How:</strong> Modify flow dependencies</p>
            <p><strong>Check:</strong> Average cycle time</p>
            <p><strong>Goal:</strong> Find optimal sequence</p>
          </div>

          <div className="reference-card">
            <div className="card-icon">📦</div>
            <h3>5. Product Release</h3>
            <p><strong>Test:</strong> Output rates</p>
            <p><strong>How:</strong> Run simulation, check metrics</p>
            <p><strong>Check:</strong> Total units, throughput</p>
            <p><strong>Goal:</strong> Meet production targets</p>
          </div>

          <div className="reference-card">
            <div className="card-icon">🚧</div>
            <h3>6. Constraints</h3>
            <p><strong>Test:</strong> Real-world limits</p>
            <p><strong>How:</strong> Set capacity, recovery times, gates</p>
            <p><strong>Check:</strong> Queue lengths, violations</p>
            <p><strong>Goal:</strong> Model realistic operations</p>
          </div>

          <div className="reference-card">
            <div className="card-icon">🔮</div>
            <h3>7. Outcome Forecasting</h3>
            <p><strong>Test:</strong> Future capacity needs</p>
            <p><strong>How:</strong> Run current + future demand</p>
            <p><strong>Check:</strong> Optimization suggestions</p>
            <p><strong>Goal:</strong> Plan for growth</p>
          </div>

          <div className="reference-card">
            <div className="card-icon">📈</div>
            <h3>8. Capacity Forecasting</h3>
            <p><strong>Test:</strong> Different capacity levels</p>
            <p><strong>How:</strong> Test 100%, 150%, 200% capacity</p>
            <p><strong>Check:</strong> Compare throughput, cost/unit</p>
            <p><strong>Goal:</strong> Find optimal investment</p>
          </div>
        </div>

        <div className="quick-tips">
          <h3>💡 Quick Tips</h3>
          <ul>
            <li><strong>Always run baseline first</strong> - Establish current state for comparison</li>
            <li><strong>Change one thing at a time</strong> - Makes it clear what caused improvements</li>
            <li><strong>Use descriptive run names</strong> - "Baseline", "Add 2 Staff", "Double Capacity"</li>
            <li><strong>Check bottleneck first</strong> - Focus optimization on the constraint</li>
            <li><strong>Red utilization = problem</strong> - Overloaded devices need capacity increase</li>
          </ul>
        </div>

        <div className="documentation-link">
          <p>📚 For detailed instructions, see <code>WHAT_IF_ANALYSIS_GUIDE.md</code></p>
        </div>
      </div>
    </div>
  );
}
