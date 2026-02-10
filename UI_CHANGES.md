# UI Changes - LiveDashboard Component

## New Metadata Section

The LiveDashboard now includes a "Run Metadata" section at the top with the following inputs:

```
┌─────────────────────────────────────────────────────────────┐
│ Simulation Control                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Run Metadata                                                 │
│ ───────────────────────────────────────────────────────────│
│                                                              │
│ Simulation Name: [Platelet Processing            ]          │
│ Run Name:        [Baseline Test                  ]          │
│                                                              │
│ Export Options                                               │
│ ───────────────────────────────────────────────────────────│
│                                                              │
│ ☑ Export results to JSON file                              │
│ Export Directory: [simulation_results            ]          │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [▶ Start]  [⏸ Pause]  [⏹ Stop]                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Behavior

### Before Simulation
- All metadata fields are **editable**
- Users can enter simulation name, run name, and configure export

### During Simulation
- All metadata fields are **disabled** (greyed out)
- Pause button becomes active (in real-time mode)
- Pause toggles to "Resume" when clicked

### After Simulation  
- Fields re-enabled for next run
- Results section shows JSON export path if exported
- Metadata is displayed in results

## New Features

1. **Simulation Name Input**
   - Used for overall simulation identification
   - Included in exported filename
   - Stored in database metadata

2. **Run Name Input**
   - Used for specific run identification  
   - Included in exported filename
   - Stored in database metadata

3. **Export Options**
   - Checkbox to enable/disable JSON export
   - Text input for export directory path
   - Default: "simulation_results"

4. **Enhanced Pause/Resume**
   - Pause button now calls backend API
   - Shows "⏸ Pause" when running
   - Shows "▶ Resume" when paused
   - Only active in real-time mode

## Example Workflow

1. User enters:
   - Simulation Name: "Platelet Pooling Process"
   - Run Name: "Baseline Test v1"
   - Export Directory: "my_results"

2. User clicks "Start"

3. During simulation:
   - Fields are disabled
   - User can click "Pause" (real-time mode)
   - Simulation pauses at next event
   - Button shows "Resume"
   - User clicks "Resume"
   - Simulation continues with timing adjustment

4. After completion:
   - Results displayed
   - JSON file created:
     `my_results/Platelet_Pooling_Process_Baseline_Test_v1_sim_20260210_123456.json`
   - Database updated with metadata
   - Export path shown in results

## CSS Classes Used

- `.metadata-section` - Container for metadata inputs
- `.metadata-inputs` - Grid layout for name inputs
- `.export-options` - Container for export settings
- `.input-group` - Individual input field wrapper
- `.checkbox-group` - Checkbox input styling

## Props Added to LiveDashboard

```typescript
interface LiveDashboardProps {
  // Existing props
  config: SimulationConfig | null;
  isRunning: boolean;
  results: any;
  
  // New callback props
  onRunSimulation: () => void;
  onPause: () => void;      // NEW
  onResume: () => void;     // NEW
  isPaused: boolean;        // NEW
  
  // New metadata props
  runName: string;          // NEW
  setRunName: (name: string) => void;     // NEW
  simulationName: string;   // NEW
  setSimulationName: (name: string) => void;  // NEW
  exportToJson: boolean;    // NEW
  setExportToJson: (enabled: boolean) => void;  // NEW
  exportDirectory: string;  // NEW
  setExportDirectory: (dir: string) => void;    // NEW
}
```

## Integration with App.tsx

App component manages all metadata state and passes handlers down to LiveDashboard:

```typescript
const [runName, setRunName] = useState<string>('');
const [simulationName, setSimulationName] = useState<string>('');
const [exportToJson, setExportToJson] = useState<boolean>(true);
const [exportDirectory, setExportDirectory] = useState<string>('simulation_results');
const [simulationId, setSimulationId] = useState<string | null>(null);
const [isPaused, setIsPaused] = useState(false);

// Pass to LiveDashboard
<LiveDashboard
  runName={runName}
  setRunName={setRunName}
  simulationName={simulationName}
  setSimulationName={setSimulationName}
  exportToJson={exportToJson}
  setExportToJson={setExportToJson}
  exportDirectory={exportDirectory}
  setExportDirectory={setExportDirectory}
  isPaused={isPaused}
  onPause={handlePause}
  onResume={handleResume}
  // ... other props
/>
```

## Benefits

1. **User-Friendly**: Clear labels and intuitive layout
2. **Configurable**: Full control over export settings
3. **Integrated**: Seamlessly works with existing UI
4. **Validated**: Fields disabled during simulation prevent errors
5. **Traceable**: Metadata makes it easy to identify simulation runs
6. **Flexible**: Export can be toggled on/off as needed
