import subprocess
import sys
import os

def run_script(script_name, cwd=None):
    print(f"\n{'='*50}")
    print(f"Running: {script_name}")
    print(f"{'='*50}\n")
    try:
        # We stream the output to the console as it runs
        process = subprocess.Popen(
            [sys.executable, script_name],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
        
        if process.returncode != 0:
            print(f"Error executing {script_name}. Pipeline stopped.")
            sys.exit(1)
        else:
            print(f"\nSuccessfully finished {script_name}.")
            
    except Exception as e:
        print(f"Exception running {script_name}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    project_root = r"d:\Projects\OmniRoute"
    data_dir = os.path.join(project_root, "data")
    
    # 1. Generate Dataset
    # Since dataset_gen.py relies on standard imports and is placed inside the data directory,
    # we run it within the data directory.
    run_script("dataset_gen.py", cwd=data_dir)
    
    # 2. Ingest Data
    # ingest_data.py is at the root
    run_script("ingest_data.py", cwd=project_root)
    
    # 3. Train Model Arena
    # train_model.py is at the root
    run_script("train_model.py", cwd=project_root)
    
    print("\n" + "*"*60)
    print("[SUCCESS] E2E Pipeline Completed Successfully!")
    print("The system has fresh data and a freshly optimized model.")
    print("*"*60 + "\n")
