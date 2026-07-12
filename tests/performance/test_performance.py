import os
import tempfile
import time
import pytest
import psutil
from ml.predictors.model_manager import ModelManager
from review_engine.engine import ReviewEngine
from utils.file_utils import collect_source_files
from server.config import Config

def get_memory_usage_mb() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def generate_mock_project(directory: str, num_files: int):
    # Generates a mix of files
    for i in range(num_files):
        ext = ['.py', '.js', '.java', '.sql', '.html'][i % 5]
        name = f"file_{i}{ext}"
        code = f"""
// Mock File {i}
function doSomething{i}() {{
    var val = {i};
    return val * 10;
}}
"""
        with open(os.path.join(directory, name), "w") as f:
            f.write(code)

@pytest.mark.performance
def test_scale_performance():
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ml', 'models')
    mm = ModelManager(models_dir=models_dir)
    mm.load_all()
    
    cfg = Config()
    engine = ReviewEngine(model_manager=mm, config=cfg)
    
    # Scale test sizes
    sizes = [10, 50, 100]  # Reduced for fast CI execution but demonstrates scaling behaviour
    
    for size in sizes:
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_mock_project(temp_dir, size)
            
            # Start profiling
            start_mem = get_memory_usage_mb()
            start_time = time.time()
            
            files = collect_source_files(temp_dir, cfg)
            result = engine.analyze_project(temp_dir, files)
            
            duration = time.time() - start_time
            end_mem = get_memory_usage_mb()
            mem_diff = end_mem - start_mem
            
            print(f"\nSize: {size} files")
            print(f"Time taken: {duration:.2f}s (Avg: {duration/size:.3f}s per file)")
            print(f"Memory used: {end_mem:.1f} MB (Delta: {mem_diff:.1f} MB)")
            
            # Assertions for performance budget
            assert end_mem < 500.0, f"Memory usage exceeded 500MB: {end_mem:.1f}MB"
            assert duration / size < 0.5, f"Analysis average speed exceeds 0.5s/file: {duration/size:.3f}s"
            assert result["total_files"] == size
