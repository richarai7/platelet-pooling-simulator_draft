"""
KPI Calculator - Comprehensive metrics for simulation results
Calculates all KPIs needed for downstream function app processing
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics


class KPICalculator:
    """Calculate comprehensive KPIs from simulation results."""
    
    def __init__(self, result: Dict[str, Any], config: Dict[str, Any]):
        """
        Initialize KPI calculator.
        
        Args:
            result: Raw simulation result dictionary
            config: Simulation configuration
        """
        self.result = result
        self.config = config
        self.simulation_start = datetime.fromisoformat(result['metadata']['completed_at'])
        
    def calculate_all_kpis(self) -> Dict[str, Any]:
        """
        Calculate all KPIs for function app export.
        
        Returns:
            Dictionary with all calculated KPIs matching the field specification
        """
        
        kpis = {
            # Basic Metrics
            "total_units_created": self._total_units_created(),
            "quality_pass_rate": self._quality_pass_rate(),
            "failed_units_count": self._failed_units_count(),
            "average_cycle_time": self._average_cycle_time(),
            "current_throughput": self._current_throughput(),
            
            # Utilization Metrics
            "uniting_station_utilization": self._uniting_station_utilization(),
            "testing_lab_utilization": self._testing_lab_utilization(),
            "capacity_utilization_per_device": self._capacity_utilization_per_device(),
            
            # Processing Metrics
            "units_processed": self._units_processed(),
            "simulation_time_elapsed": self._simulation_time_elapsed(),
            "units_in_queue": self._units_in_queue(),
            "active_units_in_process": self._active_units_in_process(),
            
            # Identification
            "run_name": self._run_name(),
            "simulation_name": self._simulation_name(),
            
            # Tracking & Logging
            "unit_transfer_tracking": self._unit_transfer_tracking(),
            
            # Staff Metrics
            "staff_count": self._staff_count(),
            "staff_utilization": self._staff_utilization(),
            
            # Input/Output Rates
            "input_supply_rate": self._input_supply_rate(),
            "product_release_volume": self._product_release_volume(),
            
            # Cost Metrics
            "total_operating_cost": self._total_operating_cost(),
            "cost_per_unit": self._cost_per_unit(),
            "waste_rate": self._waste_rate(),
            "waste_cost": self._waste_cost(),
            
            # Quality & Expiry
            "expired_units": self._expired_units(),
            "test_results_breakdown": self._test_results_breakdown(),
            
            # Performance Metrics
            "peak_throughput": self._peak_throughput(),
            "avg_wait_time_per_unit": self._avg_wait_time_per_unit(),
            "time_to_first_unit": self._time_to_first_unit(),
            
            # Bottleneck Analysis
            "resource_bottleneck": self._resource_bottleneck(),
            "max_queue_length": self._max_queue_length(),
            "idle_time_percentage": self._idle_time_percentage(),
            
            # Comparison & Variance
            "comparison_to_baseline": self._comparison_to_baseline(),
            "supply_variation": self._supply_variation(),
            "constraint_violations": self._constraint_violations(),
            
            # Forecasting & Optimization
            "demand_forecast": self._demand_forecast(),
            "optimization_suggestions": self._optimization_suggestions(),
            
            # Configuration
            "processing_station_count": self._processing_station_count(),
            "testing_station_count": self._testing_station_count(),
            "scenario_parameters": self._scenario_parameters(),
            
            # Visualization Data
            "3d_visualization": self._3d_visualization_data(),
            "scenario_comparison": self._scenario_comparison_data(),
            
            # Device Health
            "device_health": self._device_health(),
            
            # Metadata
            "export_timestamp": datetime.now().isoformat(),
            "simulation_id": self.result['metadata']['simulation_id']
        }
        
        return kpis
    
    # ==================== BASIC METRICS ====================
    
    def _total_units_created(self) -> int:
        """Total platelet units successfully created."""
        return self.result['summary']['total_flows_completed']
    
    def _quality_pass_rate(self) -> float:
        """Percentage of units passing quality tests."""
        total = self._total_units_created()
        failed = self._failed_units_count()
        if total == 0:
            return 0.0
        return ((total - failed) / total) * 100
    
    def _failed_units_count(self) -> int:
        """Number of units that failed quality."""
        # Count flows that ended in FAILED state
        failed = 0
        if 'state_history' in self.result:
            for event in self.result['state_history']:
                if event.get('to_state') == 'Failed':
                    failed += 1
        return failed
    
    def _average_cycle_time(self) -> float:
        """Average time from start to unit completion (seconds)."""
        if 'flow_details' in self.result and self.result['flow_details']:
            cycle_times = [
                f['end_time'] - f['start_time']
                for f in self.result['flow_details']
                if f.get('end_time') and f.get('start_time')
            ]
            if cycle_times:
                return statistics.mean(cycle_times)
        return 0.0
    
    def _current_throughput(self) -> float:
        """Units created per hour of simulation time."""
        sim_time_hours = self.result['summary']['simulation_time_seconds'] / 3600
        if sim_time_hours == 0:
            return 0.0
        return self._total_units_created() / sim_time_hours
    
    # ==================== UTILIZATION METRICS ====================
    
    def _uniting_station_utilization(self) -> float:
        """% time uniting stations are active (based on device type)."""
        return self._device_type_utilization("workstation")
    
    def _testing_lab_utilization(self) -> float:
        """% time testing labs are active."""
        return self._device_utilization_by_id("quality")
    
    def _capacity_utilization_per_device(self) -> Dict[str, float]:
        """% of max capacity being used for each device."""
        utilization = {}
        
        for device in self.config['devices']:
            device_id = device['id']
            max_capacity = device['capacity']
            
            # Calculate based on state history
            busy_time = 0
            total_time = self.result['summary']['simulation_time_seconds']
            
            if 'state_history' in self.result:
                processing_events = [
                    e for e in self.result['state_history']
                    if e['device_id'] == device_id and e['to_state'] == 'Processing'
                ]
                busy_time = len(processing_events) * 100  # Estimate
            
            if total_time > 0:
                utilization[device_id] = (busy_time / (total_time * max_capacity)) * 100
            else:
                utilization[device_id] = 0.0
        
        return utilization
    
    def _device_type_utilization(self, device_type: str) -> float:
        """Average utilization for devices of a specific type."""
        matching_devices = [
            d['id'] for d in self.config['devices']
            if d.get('type') == device_type
        ]
        
        if not matching_devices:
            return 0.0
        
        utilizations = [
            self._capacity_utilization_per_device().get(d, 0.0)
            for d in matching_devices
        ]
        
        return statistics.mean(utilizations) if utilizations else 0.0
    
    def _device_utilization_by_id(self, device_id_pattern: str) -> float:
        """Utilization for devices matching ID pattern."""
        matching = [
            util for dev_id, util in self._capacity_utilization_per_device().items()
            if device_id_pattern in dev_id
        ]
        return statistics.mean(matching) if matching else 0.0
    
    # ==================== PROCESSING METRICS ====================
    
    def _units_processed(self) -> int:
        """Total platelet units processed (including failed)."""
        return self._total_units_created() + self._failed_units_count()
    
    def _simulation_time_elapsed(self) -> float:
        """Simulated time elapsed (seconds)."""
        return self.result['summary']['simulation_time_seconds']
    
    def _units_in_queue(self) -> int:
        """Units currently waiting (at simulation end)."""
        # This would require tracking pending flows
        # For now, estimate as flows not completed
        total_flows = len(self.config['flows'])
        completed = self._total_units_created()
        return max(0, total_flows - completed)
    
    def _active_units_in_process(self) -> int:
        """Units actively being processed at simulation end."""
        if 'device_states' in self.result:
            processing_count = sum(
                1 for d in self.result['device_states']
                if d['final_state'] == 'Processing'
            )
            return processing_count
        return 0
    
    # ==================== IDENTIFICATION ====================
    
    def _run_name(self) -> str:
        """Name of run."""
        return self.config.get('run_name', self.result['metadata']['simulation_id'])
    
    def _simulation_name(self) -> str:
        """Name of simulation."""
        return self.config.get('scenario_name', 'Platelet Pooling Simulation')
    
    # ==================== TRACKING ====================
    
    def _unit_transfer_tracking(self) -> List[Dict[str, Any]]:
        """Log of units moving between devices."""
        transfers = []
        
        if 'flow_details' in self.result:
            for flow in self.result['flow_details']:
                # Find corresponding flow config
                flow_config = next(
                    (f for f in self.config['flows'] if f['flow_id'] == flow['flow_id']),
                    None
                )
                
                if flow_config:
                    transfers.append({
                        'unit_id': flow['flow_id'],
                        'from_device': flow_config['from_device'],
                        'to_device': flow_config['to_device'],
                        'transfer_time': flow.get('start_time', 0),
                        'completion_time': flow.get('end_time', 0)
                    })
        
        return transfers
    
    # ==================== STAFF METRICS ====================
    
    def _staff_count(self) -> int:
        """Number of staff/technicians working."""
        return self.config.get('staff_count', 0)
    
    def _staff_utilization(self) -> float:
        """% time staff actively working."""
        # Placeholder - would need staff tracking in config
        return self.config.get('staff_utilization', 0.0)
    
    # ==================== INPUT/OUTPUT RATES ====================
    
    def _input_supply_rate(self) -> float:
        """Platelet units arriving per hour."""
        sim_time_hours = self._simulation_time_elapsed() / 3600
        if sim_time_hours == 0:
            return 0.0
        
        # Count flows with no dependencies (entry points)
        entry_flows = sum(
            1 for f in self.config['flows']
            if not f.get('dependencies')
        )
        
        return entry_flows / sim_time_hours
    
    def _product_release_volume(self) -> int:
        """Units released for use."""
        return self._total_units_created() - self._expired_units()
    
    # ==================== COST METRICS ====================
    
    def _total_operating_cost(self) -> float:
        """Total cost for simulation period."""
        labor_cost = self.config.get('labor_cost', 0)
        material_cost = self.config.get('material_cost', 0) * self._units_processed()
        overhead = self.config.get('overhead_cost', 0)
        
        return labor_cost + material_cost + overhead
    
    def _cost_per_unit(self) -> float:
        """Operating cost per unit."""
        total_cost = self._total_operating_cost()
        units = self._total_units_created()
        
        if units == 0:
            return 0.0
        
        return total_cost / units
    
    def _waste_rate(self) -> float:
        """% of production wasted."""
        failed = self._failed_units_count()
        expired = self._expired_units()
        total = self._units_processed()
        
        if total == 0:
            return 0.0
        
        return ((failed + expired) / total) * 100
    
    def _waste_cost(self) -> float:
        """Financial impact of wasted units."""
        wasted_units = self._failed_units_count() + self._expired_units()
        cost_per_unit = self.config.get('cost_per_unit', 0)
        
        return wasted_units * cost_per_unit
    
    # ==================== QUALITY & EXPIRY ====================
    
    def _expired_units(self) -> int:
        """Units that aged out before uniting."""
        # Placeholder - would need time-in-queue tracking
        return 0
    
    def _test_results_breakdown(self) -> Dict[str, int]:
        """Detailed quality test results."""
        return {
            'passed': self._total_units_created(),
            'failed': self._failed_units_count(),
            'reasons': {}  # Could be expanded with failure reasons
        }
    
    # ==================== PERFORMANCE METRICS ====================
    
    def _peak_throughput(self) -> float:
        """Maximum throughput achieved (units/hour)."""
        # Would need windowed analysis of flow completion times
        # For now, use overall throughput
        return self._current_throughput()
    
    def _avg_wait_time_per_unit(self) -> float:
        """Average time units wait in queue."""
        # Difference between arrival and processing start
        if 'flow_details' in self.result:
            wait_times = []
            for flow in self.result['flow_details']:
                # Estimate wait as difference from ideal start time
                if flow.get('start_time'):
                    wait_times.append(flow['start_time'])
            
            if wait_times:
                return statistics.mean(wait_times)
        
        return 0.0
    
    def _time_to_first_unit(self) -> float:
        """Time until first unit completed."""
        if 'flow_details' in self.result:
            completion_times = [
                f['end_time'] for f in self.result['flow_details']
                if f.get('end_time')
            ]
            if completion_times:
                return min(completion_times)
        
        return 0.0
    
    # ==================== BOTTLENECK ANALYSIS ====================
    
    def _resource_bottleneck(self) -> str:
        """Identified bottleneck resource."""
        # Find device with highest utilization or longest queue
        utilizations = self._capacity_utilization_per_device()
        
        if utilizations:
            bottleneck = max(utilizations.items(), key=lambda x: x[1])
            return bottleneck[0]
        
        return "None identified"
    
    def _max_queue_length(self) -> int:
        """Maximum queue size reached."""
        # Would need queue tracking
        return self._units_in_queue()
    
    def _idle_time_percentage(self) -> Dict[str, float]:
        """% time each resource is idle."""
        idle_pct = {}
        
        for device_id, util in self._capacity_utilization_per_device().items():
            idle_pct[device_id] = 100 - util
        
        return idle_pct
    
    # ==================== COMPARISON & VARIANCE ====================
    
    def _comparison_to_baseline(self) -> Dict[str, float]:
        """Comparison vs baseline throughput."""
        baseline = self.config.get('baseline_throughput', 0)
        current = self._current_throughput()
        
        if baseline == 0:
            return {'current': current, 'baseline': 0, 'difference': 0}
        
        return {
            'current': current,
            'baseline': baseline,
            'difference_pct': ((current - baseline) / baseline) * 100
        }
    
    def _supply_variation(self) -> float:
        """Fluctuation in arrival rate (std dev %)."""
        # Would need arrival time tracking
        return 0.0
    
    def _constraint_violations(self) -> int:
        """Count of constraint limit breaches."""
        # Would need constraint tracking
        return 0
    
    # ==================== FORECASTING & OPTIMIZATION ====================
    
    def _demand_forecast(self) -> Dict[str, float]:
        """Projected future demand."""
        current = self._current_throughput()
        
        return {
            'current_rate': current,
            'projected_demand': current * 1.1,  # 10% growth assumption
            'variance': current * 0.1
        }
    
    def _optimization_suggestions(self) -> List[str]:
        """Recommended process changes."""
        suggestions = []
        
        bottleneck = self._resource_bottleneck()
        if bottleneck != "None identified":
            suggestions.append(f"Increase capacity at {bottleneck}")
        
        waste_rate = self._waste_rate()
        if waste_rate > 10:
            suggestions.append(f"Reduce waste rate (currently {waste_rate:.1f}%)")
        
        utilizations = self._capacity_utilization_per_device()
        for device, util in utilizations.items():
            if util < 30:
                suggestions.append(f"Consider reducing {device} capacity (only {util:.1f}% utilized)")
        
        return suggestions
    
    # ==================== CONFIGURATION ====================
    
    def _processing_station_count(self) -> int:
        """Number of uniting stations."""
        return sum(
            1 for d in self.config['devices']
            if d.get('type') == 'workstation'
        )
    
    def _testing_station_count(self) -> int:
        """Number of testing labs."""
        return sum(
            1 for d in self.config['devices']
            if 'quality' in d['id'] or 'test' in d['id']
        )
    
    def _scenario_parameters(self) -> Dict[str, Any]:
        """Configuration parameters."""
        return {
            'duration': self.config['simulation']['duration'],
            'random_seed': self.config['simulation']['random_seed'],
            'execution_mode': self.config['simulation']['execution_mode'],
            'device_count': len(self.config['devices']),
            'flow_count': len(self.config['flows'])
        }
    
    # ==================== VISUALIZATION DATA ====================
    
    def _3d_visualization_data(self) -> Dict[str, Any]:
        """Data for 3D visualization."""
        # Device positions and flow data
        devices = []
        
        for i, device in enumerate(self.config['devices']):
            devices.append({
                'id': device['id'],
                'type': device.get('type', 'machine'),
                'position': [i * 100, 0, 0],  # Simple linear layout
                'capacity': device['capacity'],
                'utilization': self._capacity_utilization_per_device().get(device['id'], 0)
            })
        
        return {
            'devices': devices,
            'flows': [
                {
                    'from': f['from_device'],
                    'to': f['to_device'],
                    'id': f['flow_id']
                }
                for f in self.config['flows'][:10]  # Limit for visualization
            ]
        }
    
    def _scenario_comparison_data(self) -> Dict[str, Any]:
        """Multi-scenario comparison KPIs."""
        return {
            'scenario_id': self.result['metadata']['simulation_id'],
            'throughput': self._current_throughput(),
            'cycle_time': self._average_cycle_time(),
            'utilization': statistics.mean(self._capacity_utilization_per_device().values())
                if self._capacity_utilization_per_device() else 0,
            'cost_per_unit': self._cost_per_unit()
        }
    
    # ==================== DEVICE HEALTH ====================
    
    def _device_health(self) -> Dict[str, str]:
        """Device health status."""
        health = {}
        
        if 'device_states' in self.result:
            for device in self.result['device_states']:
                device_id = device['device_id']
                final_state = device['final_state']
                
                if final_state == 'Failed':
                    health[device_id] = 'Critical'
                elif final_state == 'Blocked':
                    health[device_id] = 'Warning'
                else:
                    health[device_id] = 'Healthy'
        
        return health
