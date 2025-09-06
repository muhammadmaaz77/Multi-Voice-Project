"""
Background task worker for Phase 5B
Handles various background processing tasks.
"""
import asyncio
from typing import Dict, List, Any, Callable
from datetime import datetime
import json

class BackgroundTaskWorker:
    """Generic background task worker."""
    
    def __init__(self):
        self.tasks = {}
        self.task_handlers = {}
        self.is_running = False
        self.max_concurrent_tasks = 5
        self.running_tasks = set()
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a task handler for a specific task type."""
        self.task_handlers[task_type] = handler
        print(f"Registered handler for task type: {task_type}")
    
    async def start(self):
        """Start the background worker."""
        self.is_running = True
        print("Background task worker started")
        
        # Start background task processing
        asyncio.create_task(self._process_task_queue())
    
    async def stop(self):
        """Stop the background worker."""
        self.is_running = False
        
        # Wait for running tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks, return_exceptions=True)
        
        print("Background task worker stopped")
    
    async def queue_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """Queue a new background task."""
        task_id = f"task_{task_type}_{datetime.now().timestamp()}"
        
        self.tasks[task_id] = {
            "task_id": task_id,
            "task_type": task_type,
            "task_data": task_data,
            "status": "queued",
            "progress": 0.0,
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None
        }
        
        print(f"Queued task {task_id} of type {task_type}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a background task."""
        return self.tasks.get(task_id, {"error": "Task not found"})
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a queued or running task."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task["status"] in ["queued", "running"]:
            task["status"] = "cancelled"
            task["completed_at"] = datetime.now().isoformat()
            return True
        
        return False
    
    async def _process_task_queue(self):
        """Process tasks in the background."""
        while self.is_running:
            # Check if we can run more tasks
            if len(self.running_tasks) < self.max_concurrent_tasks:
                # Find next queued task
                next_task = None
                for task_id, task in self.tasks.items():
                    if task["status"] == "queued":
                        next_task = (task_id, task)
                        break
                
                if next_task:
                    task_id, task = next_task
                    # Start the task
                    task_coroutine = self._execute_task(task_id, task)
                    task_future = asyncio.create_task(task_coroutine)
                    self.running_tasks.add(task_future)
            
            # Clean up completed tasks
            completed_tasks = [task for task in self.running_tasks if task.done()]
            for task in completed_tasks:
                self.running_tasks.remove(task)
            
            await asyncio.sleep(1)  # Check every second
    
    async def _execute_task(self, task_id: str, task: Dict[str, Any]):
        """Execute a single task."""
        try:
            task_type = task["task_type"]
            
            if task_type not in self.task_handlers:
                raise ValueError(f"No handler registered for task type: {task_type}")
            
            task["status"] = "running"
            task["started_at"] = datetime.now().isoformat()
            
            print(f"Executing task {task_id} of type {task_type}")
            
            # Execute the task handler
            handler = self.task_handlers[task_type]
            result = await handler(task["task_data"], self._progress_callback(task_id))
            
            task["status"] = "completed"
            task["result"] = result
            task["progress"] = 1.0
            task["completed_at"] = datetime.now().isoformat()
            
            print(f"Completed task {task_id}")
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["completed_at"] = datetime.now().isoformat()
            print(f"Task {task_id} failed: {e}")
    
    def _progress_callback(self, task_id: str):
        """Create a progress callback for a specific task."""
        def update_progress(progress: float):
            if task_id in self.tasks:
                self.tasks[task_id]["progress"] = min(1.0, max(0.0, progress))
        
        return update_progress
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        stats = {
            "total_tasks": len(self.tasks),
            "running_tasks": len(self.running_tasks),
            "is_running": self.is_running,
            "max_concurrent": self.max_concurrent_tasks,
            "registered_handlers": list(self.task_handlers.keys())
        }
        
        # Count by status
        status_counts = {}
        for task in self.tasks.values():
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        stats["status_counts"] = status_counts
        return stats

# Example task handlers for Phase 5B
async def audio_processing_task(task_data: Dict[str, Any], progress_callback: Callable):
    """Example audio processing task handler."""
    # Simulate audio processing
    for i in range(10):
        await asyncio.sleep(0.5)
        progress_callback(i / 10)
    
    return {"processed": True, "duration": 5.0}

async def translation_task(task_data: Dict[str, Any], progress_callback: Callable):
    """Example translation task handler."""
    text = task_data.get("text", "")
    target_lang = task_data.get("target_language", "es")
    
    # Simulate translation processing
    for i in range(5):
        await asyncio.sleep(0.3)
        progress_callback(i / 5)
    
    return {
        "original_text": text,
        "translated_text": f"[Translated to {target_lang}] {text}",
        "target_language": target_lang
    }

# Global worker instance
background_worker = BackgroundTaskWorker()

# Register example handlers
background_worker.register_handler("audio_processing", audio_processing_task)
background_worker.register_handler("translation", translation_task)
