# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import os
import shutil
import compileall
import zipapp
import tempfile


SOURCE_DIR = os.path.abspath("as64")  
PLUGIN_DIR = os.path.abspath("plugins")

OUTPUT_DIR = os.path.abspath("as64.dist")
OUTPUT_ARCHIVE = os.path.join(OUTPUT_DIR, "as64")

ENTRY_MODULE = "as64.coordinator"


def generate_main(entry_module):   
    source = "import runpy\n"
    source += f"runpy.run_module('{entry_module}', run_name='__main__')"

    return source


def archive_filter(path):
    if path.name == '__main__.py':
        return True
    return not path.name.endswith('.py')


def move_pyc_files(build_dir):
    for root, dirs, files in os.walk(build_dir):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            for filename in os.listdir(pycache_dir):
                if filename.endswith('.pyc'):
                    module_name = filename.split('.')[0]
                    new_filename = module_name + '.pyc'
                    shutil.move(os.path.join(pycache_dir, filename), os.path.join(root, new_filename))
            shutil.rmtree(pycache_dir)
            

def _compile_as64():
    build_dir = tempfile.mkdtemp(prefix="as64.build")
    
    try:
        # Copy source dir
        dest_source_dir = os.path.join(build_dir, os.path.basename(SOURCE_DIR))
        shutil.copytree(SOURCE_DIR, dest_source_dir)
        
        # Compile
        compileall.compile_dir(build_dir, force=True)
        
        #
        move_pyc_files(build_dir)
        
        # Generate entry point
        main_py = os.path.join(build_dir, "__main__.py")
        with open(main_py, "w", encoding="utf-8") as f:
            f.write(generate_main(ENTRY_MODULE))
        
        # Archive from build directory
        zipapp.create_archive(build_dir, target=OUTPUT_ARCHIVE, filter=archive_filter)
    
    finally:
        shutil.rmtree(build_dir)
            
            
def _compile_plugins():
    temp_plugin_dir = tempfile.mkdtemp(prefix="plugins.build")
    
    try:
        # Copy plugin dir
        dest_plugins_dir = os.path.join(temp_plugin_dir, "plugins")
        shutil.copytree(PLUGIN_DIR, dest_plugins_dir)
        
        # Compile
        compileall.compile_dir(dest_plugins_dir, force=True)
        
        #
        move_pyc_files(dest_plugins_dir)
        
        #
        for root, dirs, files in os.walk(dest_plugins_dir):
            for f in files:
                if f.endswith('.py'):
                    os.remove(os.path.join(root, f))
        
        # Copy to output dir
        final_plugins_dir = os.path.join(OUTPUT_DIR, "plugins")
        if os.path.exists(final_plugins_dir):
            shutil.rmtree(final_plugins_dir)
        shutil.copytree(dest_plugins_dir, final_plugins_dir)
    finally:
        shutil.rmtree(temp_plugin_dir)


def build():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    _compile_as64()
    _compile_plugins()
    

if __name__ == "__main__":
    build()
