import os
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

replacements = {
    r"@/components/AnalysisPanel\b": "@/components/features/AnalysisPanel",
    r"@/components/FileUpload\b": "@/components/features/FileUpload",
    r"@/components/RecommendationsPanel\b": "@/components/features/RecommendationsPanel",
    r"@/components/ScoreChart\b": "@/components/features/ScoreChart",
    
    r"@/components/NetworkMonitor\b": "@/components/layout/NetworkMonitor",
    r"@/components/Sidebar\b": "@/components/layout/Sidebar",
    r"@/components/Providers\b": "@/components/layout/Providers",
    
    # Relative imports from within components/ or app/
    r"from ['\"](?:\.\./)*components/AnalysisPanel['\"]": "from '@/components/features/AnalysisPanel'",
    r"from ['\"](?:\.\./)*components/FileUpload['\"]": "from '@/components/features/FileUpload'",
    r"from ['\"](?:\.\./)*components/RecommendationsPanel['\"]": "from '@/components/features/RecommendationsPanel'",
    r"from ['\"](?:\.\./)*components/ScoreChart['\"]": "from '@/components/features/ScoreChart'",
    
    r"from ['\"](?:\.\./)*components/NetworkMonitor['\"]": "from '@/components/layout/NetworkMonitor'",
    r"from ['\"](?:\.\./)*components/Sidebar['\"]": "from '@/components/layout/Sidebar'",
    r"from ['\"](?:\.\./)*components/Providers['\"]": "from '@/components/layout/Providers'",
}

for root, dirs, files in os.walk(base_dir):
    if ".next" in dirs:
        dirs.remove(".next")
    if "node_modules" in dirs:
        dirs.remove("node_modules")
    if "node_modules_old" in dirs:
        dirs.remove("node_modules_old")
        
    for file in files:
        if file.endswith((".ts", ".tsx")):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue
                
            new_content = content
            for old_pattern, new_string in replacements.items():
                new_content = re.sub(old_pattern, new_string, new_content)
                
            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated imports in {filepath}")

print("Frontend import refactoring complete.")
