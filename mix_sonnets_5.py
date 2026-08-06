import shutil
import os
import random

def get_file_list(directory):
    """Return a list of files in the specified directory."""
    try:
        return [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
    except FileNotFoundError:
        return []

def create_sequence(real_dir, fake_dir, total=154):
    real_files = get_file_list(real_dir)
    fake_files = get_file_list(fake_dir)

    # Calculate fake target first, then subtract from total 
    # This guarantees the sum of targets always equals your total
    fake_target = total // 5
    real_target = total - fake_target

    for attempt in range(1000):
        random.shuffle(real_files)
        random.shuffle(fake_files)
        
        sequence = {}
        used_basenames = set()

        # Select real files at 80%
        real_selected = []
        for file in real_files:
            basename = os.path.basename(file)
            if basename not in used_basenames:
                used_basenames.add(basename)
                real_selected.append(file)
                if len(real_selected) == real_target:
                    break

        # Select fake files at 20%
        fake_selected = []
        for file in fake_files:
            basename = os.path.basename(file)
            if basename not in used_basenames:
                used_basenames.add(basename)
                fake_selected.append(file)
                if len(fake_selected) == fake_target:
                    break

        if len(real_selected) == real_target and len(fake_selected) == fake_target:
            # FIX: Changed i to i+1 so your printed keys match actual human counts
            for i, file in enumerate(real_selected):
                sequence[f"real_{i+1}"] = file
            for i, file in enumerate(fake_selected):
                sequence[f"fake_{i+1}"] = file
            return sequence

    # FIX: Explicit warning if duplicate basenames forced a fallback failure
    print(f"\n[WARNING] Could not find enough unique files after 1000 retries.")
    print(f"Expected: Real={real_target}, Fake={fake_target}")
    print(f"Gained:   Real={len(real_selected)}, Fake={len(fake_selected)}\n")

    sequence = {}
    for i, file in enumerate(real_selected):
        sequence[f"real_{i+1}"] = file
    for i, file in enumerate(fake_selected):
        sequence[f"fake_{i+1}"] = file
    return sequence


def write_mix_sequence(sequence, target_directory, verbose=True):
    """
    Copies files from the sequence dictionary into the target directory.
    """
    if verbose:
        print(f"Starting copy of {len(sequence)} files to '{target_directory}'...")
    
    for key, src_path in sequence.items():
        dest_dir = os.path.join(target_directory)
        
        # Ensure the destination folder exists
        os.makedirs(dest_dir, exist_ok=True)
        
        # Copy the file
        try:
            shutil.copy(src_path, dest_dir)
            if verbose:
                print("copying: ", src_path )
        except IOError as e:
            print(f"[ERROR] Failed to copy {src_path}: {e}")
    
    if verbose:
        print("Copy complete!")

# Example usage
real_dir = "data"  
fake_dir = "fake_sonnet" 
mix_dir = "mix_sonnet" 

sequence = create_sequence(real_dir, fake_dir, total=154)

# Print the sequence in the format expected by mix_compare_results.py
for key, value in sequence.items():
    print(f"copying:  {value}")

write_mix_sequence( sequence, mix_dir, verbose=False )

# Quick sanity check printout
print(f"\n--- Verification ---")
print(f"Total files in final sequence: {len(sequence)}")
