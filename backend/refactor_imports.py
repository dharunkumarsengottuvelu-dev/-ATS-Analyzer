import os
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

replacements = {
    r"from backend\.analyzer\b": "from backend.ai.analyzer",
    r"import backend\.analyzer\b": "import backend.ai.analyzer",
    
    r"from backend\.embeddings\b": "from backend.ai.embeddings",
    r"import backend\.embeddings\b": "import backend.ai.embeddings",
    
    r"from backend\.ocr\b": "from backend.ai.ocr",
    r"import backend\.ocr\b": "import backend.ai.ocr",
    
    r"from backend\.parser\b": "from backend.ai.parser",
    r"import backend\.parser\b": "import backend.ai.parser",
    
    r"from backend\.prompts\b": "from backend.ai.prompts",
    r"import backend\.prompts\b": "import backend.ai.prompts",
    
    r"from backend\.scoring\b": "from backend.ai.scoring",
    r"import backend\.scoring\b": "import backend.ai.scoring",
    
    r"from backend\.services\.recommendation\b": "from backend.ai.recommendation",
    r"import backend\.services\.recommendation\b": "import backend.ai.recommendation",
    
    # API routes refactor
    r"from backend\.api\b(?!\.v1\.routes)": "from backend.api.v1.routes",
    r"import backend\.api\b(?!\.v1\.routes)": "import backend.api.v1.routes",
}

for root, dirs, files in os.walk(base_dir):
    if ".venv" in dirs:
        dirs.remove(".venv")
    if ".venv_old" in dirs:
        dirs.remove(".venv_old")
    if "__pycache__" in dirs:
        dirs.remove("__pycache__")
        
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="latin-1") as f:
                    content = f.read()
                
            new_content = content
            for old_pattern, new_string in replacements.items():
                new_content = re.sub(old_pattern, new_string, new_content)
                
            if new_content != content:
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                except Exception:
                    with open(filepath, "w", encoding="latin-1") as f:
                        f.write(new_content)
                print(f"Updated imports in {filepath}")

print("Import refactoring complete.")
