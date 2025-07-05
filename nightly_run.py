#!/usr/bin/env python3
"""Main entry point for overnight research runs."""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

import yaml

from src.research_engine import ResearchEngine
from src.file_monitor import FileMonitor
from src.thermal_monitor import ThermalMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/research_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NightlyResearcher:
    """Main application for overnight research."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the nightly researcher."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Initialize components
        self.research_engine = ResearchEngine(config_path)
        self.file_monitor = FileMonitor(self.config)
        self.thermal_monitor = ThermalMonitor(self.config)
        
        # Control flags
        self.running = True
        self.current_task = None
        
    async def run(self):
        """Main run loop."""
        logger.info("Starting AI Researcher - Overnight Mode")
        logger.info(f"Monitoring: {self.config['localsend']['input_path']}")
        logger.info(f"Output to: {self.config['localsend']['output_path']}")
        
        # Start file monitoring
        self.file_monitor.start()
        
        # Main processing loop
        while self.running:
            try:
                # Check thermals
                thermal_status = self.thermal_monitor.check_thermals()
                if not thermal_status['safe']:
                    logger.warning(f"Thermal warning: {thermal_status['warnings']}")
                    await asyncio.sleep(60)  # Cool down period
                    continue
                    
                # Get next assignment
                assignment_path = await self.file_monitor.get_next_assignment()
                
                if assignment_path:
                    logger.info(f"Processing assignment: {assignment_path}")
                    self.current_task = asyncio.create_task(
                        self._process_assignment(assignment_path)
                    )
                    await self.current_task
                else:
                    # No assignment, log status
                    usage = self.thermal_monitor.get_resource_usage()
                    logger.debug(
                        f"Idle - CPU: {usage['cpu_percent']:.1f}% "
                        f"GPU: {usage['gpu_percent']:.1f}% "
                        f"Temp: {thermal_status['cpu_temp']:.1f}°C"
                    )
                    
            except asyncio.CancelledError:
                logger.info("Received shutdown signal")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(60)
                
        # Cleanup
        self.file_monitor.stop()
        logger.info("AI Researcher stopped")
        
    async def _process_assignment(self, assignment_path: Path):
        """Process a single research assignment."""
        start_time = datetime.now()
        
        try:
            # Run research
            reports = await self.research_engine.process_assignment(assignment_path)
            
            # Save reports to LocalSend
            for report in reports:
                output_path = self.file_monitor.save_report(report)
                logger.info(f"Report saved: {output_path}")
                
            # Log completion
            duration = (datetime.now() - start_time).total_seconds() / 60
            logger.info(f"Assignment completed in {duration:.1f} minutes")
            
            # Move processed assignment
            processed_dir = assignment_path.parent / 'processed'
            processed_dir.mkdir(exist_ok=True)
            assignment_path.rename(processed_dir / assignment_path.name)
            
        except Exception as e:
            logger.error(f"Error processing assignment: {e}", exc_info=True)
            
            # Save error report
            error_report = Path('output') / f"ERROR_{assignment_path.stem}_{datetime.now():%Y%m%d_%H%M}.txt"
            error_report.parent.mkdir(exist_ok=True)
            error_report.write_text(f"Error processing {assignment_path}:\n{str(e)}")
            self.file_monitor.save_report(error_report)
            
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown."""
        logger.info("Initiating shutdown...")
        self.running = False
        
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()


async def main():
    """Main entry point."""
    # Create necessary directories
    for dir_name in ['logs', 'output', 'checkpoints']:
        Path(dir_name).mkdir(exist_ok=True)
        
    # Check for config
    if not Path('config.yaml').exists():
        logger.error("config.yaml not found! Copy config.example.yaml and update it.")
        sys.exit(1)
        
    # Create and run researcher
    researcher = NightlyResearcher()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, researcher.shutdown)
    signal.signal(signal.SIGTERM, researcher.shutdown)
    
    # Run
    await researcher.run()


if __name__ == "__main__":
    asyncio.run(main())