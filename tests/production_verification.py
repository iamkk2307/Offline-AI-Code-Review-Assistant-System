"""
Complete Production End-To-End Verification
===========================================
Creates a multi-language test project with files in all 13 supported languages,
runs a full hybrid analysis with ML inference and static analysis rules,
and generates reports in HTML, PDF, MD, JSON, and CSV formats.
"""

import os
import sys
import tempfile
import time
import psutil
from pathlib import Path

# Insert project root into system path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from ml.predictors.model_manager import ModelManager
from review_engine.engine import ReviewEngine
from utils.file_utils import collect_source_files
from database.db import init_db, get_session
from database.repository import ProjectRepository, AnalysisRepository
from reports.report_factory import ReportFactory


# Sample source files for all 13 supported languages
MOCK_FILES = {
    # 1. Python
    "main.py": """
import sys
def compute(data):
    # TODO: optimize logic
    eval(data)
    password = "admin_password123"
    return data
""",
    # 2. Java
    "Service.java": """
import java.util.*;
public class Service {
    public void query(String input) {
        System.out.println("Processing: " + input);
        try {
            // empty catch block
        } catch (Exception e) {}
    }
}
""",
    # 3. JavaScript
    "app.js": """
function loadData(url) {
  var data = fetch(url);
  eval(data);
  return data;
}
""",
    # 4. TypeScript
    "utils.ts": """
interface Config {
  url: string;
}
export function getConfig(arg: any): Config {
  return arg as any;
}
""",
    # 5. C
    "helper.c": """
#include <stdio.h>
#include <string.h>
void read_input() {
    char buf[8];
    gets(buf);
}
""",
    # 6. C++
    "engine.cpp": """
#include <iostream>
using namespace std;
int main() {
    int* data = new int[10];
    return 0;
}
""",
    # 7. C#
    "Program.cs": """
using System;
namespace App {
    class Program {
        static void Main() {
            try {
                Console.WriteLine("Started");
            } catch (Exception e) {}
        }
    }
}
""",
    # 8. PHP
    "index.php": """
<?php
$user = $_GET['user'];
echo "Welcome " . $user;
mysql_query("SELECT * FROM users WHERE name = '" . $user . "'");
""",
    # 9. HTML
    "index.html": """
<!DOCTYPE html>
<html>
<head><title>Test App</title></head>
<body>
    <img src="logo.png">
    <script>eval("alert(1)")</script>
</body>
</html>
""",
    # 10. CSS
    "styles.css": """
.body {
  background-color: #fff !important;
}
#header {
  margin: 10pxpx;
}
""",
    # 11. SQL
    "schema.sql": """
SELECT * FROM users WHERE active = 1;
GRANT ALL PRIVILEGES ON db TO root;
""",
    # 12. Bash
    "deploy.sh": """
#!/bin/bash
chmod 777 run.sh
curl -k https://insecure-site.com
""",
    # 13. JSON
    "config.json": """
{
  "api_token": "xoxb-1234567890-abcdef",
  "port": 8080
}
"""
}


def run_production_verification():
    print("=" * 70)
    print("🚀 OFFLINE CODE REVIEW ASSISTANT — PRODUCTION VERIFICATION PASS")
    print("=" * 70)
    
    # 1. Verify ML models load successfully
    print("\n[1/6] Loading pre-trained ML models...")
    models_dir = os.path.join(ROOT_DIR, 'ml', 'models')
    mm = ModelManager(models_dir=models_dir)
    start_t = time.time()
    mm.load_all()
    assert mm.is_ready, "ML Model Manager failed to load models!"
    assert mm.model_count == 6, f"Expected 6 models, found {mm.model_count}"
    print(f"✓ All 6 models loaded successfully in {time.time() - start_t:.3f}s")
    
    # 2. Setup mock multi-language project
    print("\n[2/6] Generating mock project with all 13 supported languages...")
    temp_project = tempfile.TemporaryDirectory()
    project_path = temp_project.name
    
    for filename, code in MOCK_FILES.items():
        with open(os.path.join(project_path, filename), "w", encoding='utf-8') as f:
            f.write(code.strip())
            
    print(f"✓ Mock project populated at: {project_path}")
    
    # 3. Setup SQLite db and insert project
    print("\n[3/6] Initializing local database and registering project...")
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_url = f"sqlite:///{db_file.name}"
    init_db(db_url)
    
    session = get_session()
    proj_repo = ProjectRepository(session)
    project = proj_repo.create(name="E2E Verify Project", path=project_path)
    session.commit()
    assert project.id is not None
    print(f"✓ Project registered in database with ID {project.id}")
    
    # 4. Run Review Engine Analysis
    print("\n[4/6] Running hybrid review pipeline on all files...")
    engine = ReviewEngine(model_manager=mm)
    
    from server.config import Config
    files = collect_source_files(project_path, Config())
    assert len(files) == 13, f"Expected 13 source files, collected {len(files)}"
    
    start_t = time.time()
    results = engine.analyze_project(project_path, files)
    elapsed = time.time() - start_t
    
    print(f"✓ Project analysis complete: analyzed {results['analyzed_files']} files")
    print(f"✓ Average analysis throughput: {elapsed/13:.3f} seconds/file")
    
    # Verify scores and issues are generated
    scores = results["scores"]
    print(f"  - Overall health score: {scores['overall']:.1f}")
    print(f"  - Quality score:        {scores['quality']:.1f}")
    print(f"  - Security score:       {scores['security']:.1f}")
    print(f"  - Maintainability score: {scores['maintainability']:.1f}")
    
    issue_sum = results["issue_summary"]
    print(f"  - Total Issues Found:   {issue_sum['total']}")
    print(f"  - Critical Issues:      {issue_sum['critical']}")
    print(f"  - High Issues:          {issue_sum['high']}")
    print(f"  - Medium Issues:        {issue_sum['medium']}")
    assert issue_sum["total"] > 0, "No issues detected!"
    
    # 5. Export Reports
    print("\n[5/6] Generating reports in all 5 supported formats...")
    report_formats = ['html', 'pdf', 'markdown', 'json', 'csv']
    output_dir = tempfile.mkdtemp()
    
    for fmt in report_formats:
        generator = ReportFactory.create(fmt)
        out_path = generator.generate(results, output_dir)
        assert os.path.exists(out_path), f"Report {fmt} was not created!"
        print(f"✓ Generated {fmt.upper()} report at: {out_path}")
        
    # 6. Verify resources & performance limits
    print("\n[6/6] Checking system constraints and memory consumption...")
    process = psutil.Process(os.getpid())
    rss_mb = process.memory_info().rss / (1024 * 1024)
    print(f"✓ Final process RSS memory usage: {rss_mb:.1f} MB (Budget limit: 500 MB)")
    assert rss_mb < 500.0, "Memory budget exceeded!"
    
    print("\n" + "=" * 70)
    print("🎉 ALL PRODUCTION VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)
    
    # Cleanups
    session.close()
    try:
        os.remove(db_file.name)
        temp_project.cleanup()
    except Exception:
        pass


if __name__ == '__main__':
    run_production_verification()
