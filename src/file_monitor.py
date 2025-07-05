"""Monitor LocalSend folder for new research assignments."""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Set

import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

logger = logging.getLogger(__name__)


class AssignmentHandler(FileSystemEventHandler):
    """Handle new assignment files in LocalSend folder."""
    
    def __init__(self, queue: asyncio.Queue):
        """Initialize the handler with an async queue."""
        self.queue = queue
        self.processed_files: Set[Path] = set()
        
    def on_created(self, event: FileCreatedEvent):
        """Handle new file creation events."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Check if it's a YAML assignment file
        if file_path.suffix in ['.yaml', '.yml'] and file_path not in self.processed_files:
            logger.info(f"New assignment detected: {file_path}")
            
            # Validate it's a research assignment
            if self._is_valid_assignment(file_path):
                # Add to queue for processing
                asyncio.create_task(self._add_to_queue(file_path))
                self.processed_files.add(file_path)
            else:
                logger.warning(f"Invalid assignment format: {file_path}")
                
    def _is_valid_assignment(self, file_path: Path) -> bool:
        """Check if file is a valid research assignment."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                
            # Check for required fields
            required = ['title', 'objectives']
            return all(field in data for field in required)
            
        except Exception as e:
            logger.error(f"Error validating assignment {file_path}: {e}")
            return False
            
    async def _add_to_queue(self, file_path: Path):
        """Add file to async processing queue."""
        await self.queue.put(file_path)


class FileMonitor:
    """Monitor LocalSend folder for research assignments."""
    
    def __init__(self, config: dict):
        """Initialize the file monitor."""
        self.input_path = Path(config['localsend']['input_path'])
        self.output_path = Path(config['localsend']['output_path'])
        self.check_interval = config['localsend']['check_interval']
        
        # Create paths if they don't exist
        self.input_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Assignment queue
        self.assignment_queue = asyncio.Queue()
        
        # File system observer
        self.observer = Observer()
        self.handler = AssignmentHandler(self.assignment_queue)
        
    def start(self):
        """Start monitoring for files."""
        logger.info(f"Starting file monitor on: {self.input_path}")
        
        # Check for existing assignments
        self._check_existing_assignments()
        
        # Start watching for new files
        self.observer.schedule(self.handler, str(self.input_path), recursive=False)
        self.observer.start()
        
    def stop(self):
        """Stop file monitoring."""
        self.observer.stop()
        self.observer.join()
        
    def _check_existing_assignments(self):
        """Check for any existing assignment files."""
        for file_path in self.input_path.glob('*.yaml'):
            if file_path not in self.handler.processed_files:
                if self.handler._is_valid_assignment(file_path):
                    logger.info(f"Found existing assignment: {file_path}")
                    asyncio.create_task(self.handler._add_to_queue(file_path))
                    self.handler.processed_files.add(file_path)
                    
    async def get_next_assignment(self) -> Optional[Path]:
        """Get the next assignment from the queue."""
        try:
            # Wait for assignment with timeout
            assignment = await asyncio.wait_for(
                self.assignment_queue.get(),
                timeout=self.check_interval
            )
            return assignment
        except asyncio.TimeoutError:
            return None
            
    def save_report(self, report_path: Path) -> Path:
        """Copy report to LocalSend output folder."""
        output_file = self.output_path / report_path.name
        
        # Copy file to output
        output_file.write_bytes(report_path.read_bytes())
        logger.info(f"Report saved to LocalSend: {output_file}")
        
        return output_file