"""Monitor system thermals to prevent overheating."""

import logging
import psutil
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    
logger = logging.getLogger(__name__)


class ThermalMonitor:
    """Monitor CPU and GPU temperatures."""
    
    def __init__(self, config: dict):
        """Initialize thermal monitoring."""
        self.max_cpu_temp = config['monitoring']['max_cpu_temp']
        self.max_gpu_temp = config['monitoring']['max_gpu_temp']
        self.enabled = config['monitoring']['enabled']
        
    def check_thermals(self) -> dict:
        """Check current thermal status."""
        if not self.enabled:
            return {'safe': True, 'cpu_temp': 0, 'gpu_temp': 0}
            
        status = {
            'safe': True,
            'cpu_temp': 0,
            'gpu_temp': 0,
            'warnings': []
        }
        
        # Check CPU temperature
        cpu_temp = self._get_cpu_temp()
        if cpu_temp:
            status['cpu_temp'] = cpu_temp
            if cpu_temp > self.max_cpu_temp:
                status['safe'] = False
                status['warnings'].append(f"CPU temperature too high: {cpu_temp}°C")
                
        # Check GPU temperature
        if GPU_AVAILABLE:
            gpu_temp = self._get_gpu_temp()
            if gpu_temp:
                status['gpu_temp'] = gpu_temp
                if gpu_temp > self.max_gpu_temp:
                    status['safe'] = False
                    status['warnings'].append(f"GPU temperature too high: {gpu_temp}°C")
                    
        return status
        
    def _get_cpu_temp(self) -> float:
        """Get CPU temperature."""
        try:
            # Try to get temperature sensors
            temps = psutil.sensors_temperatures()
            
            # Look for CPU temperature
            for name, entries in temps.items():
                for entry in entries:
                    if 'cpu' in entry.label.lower() or 'core' in entry.label.lower():
                        return entry.current
                        
            # If no CPU-specific sensor, use first available
            if temps:
                first_sensor = list(temps.values())[0][0]
                return first_sensor.current
                
        except Exception as e:
            logger.debug(f"Could not read CPU temperature: {e}")
            
        return None
        
    def _get_gpu_temp(self) -> float:
        """Get GPU temperature."""
        if not GPU_AVAILABLE:
            return None
            
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].temperature
        except Exception as e:
            logger.debug(f"Could not read GPU temperature: {e}")
            
        return None
        
    def get_resource_usage(self) -> dict:
        """Get current resource usage."""
        usage = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'gpu_percent': 0,
            'gpu_memory_mb': 0
        }
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    usage['gpu_percent'] = gpu.load * 100
                    usage['gpu_memory_mb'] = gpu.memoryUsed
            except:
                pass
                
        return usage