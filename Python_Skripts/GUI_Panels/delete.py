import os

def count_lines_of_code(directory):
    total_lines = 0
    for root, dirs, files in os.walk(directory):
        # Skip the build directory
        if 'build' in dirs:
            dirs.remove('build')
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
    return total_lines

if __name__ == "__main__":
    directory = "c:/Users/Valentin/Documents/GIT_REPS/MtecThesis"  # Change this to your project directory
    total_lines = count_lines_of_code(directory)
    print(f"Total lines of code: {total_lines}")