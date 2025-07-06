#!/usr/bin/env python3
"""Quick setup and test script for AI Researcher."""

import subprocess
import sys
from pathlib import Path


def check_requirements():
    """Check if basic requirements are met."""
    print("🔍 Checking requirements...\n")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        return False
    print("✅ Python version OK")
    
    # Check if Ollama is installed
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama installed")
        else:
            print("❌ Ollama not found - install from https://ollama.ai")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found - install from https://ollama.ai")
        return False
    
    # Check if model is available
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'dolphin3:latest' in result.stdout:
            print("✅ Dolphin model available")
        else:
            print("⚠️  Dolphin model not found")
            print("   Run: ollama pull dolphin3:latest")
            return False
    except:
        pass
    
    return True


def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")
    
    dirs = ['logs', 'output', 'checkpoints', 'processed']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"   ✅ Created {dir_name}/")


def create_config():
    """Create config.yaml if it doesn't exist."""
    if not Path('config.yaml').exists():
        print("\n⚙️  Creating config.yaml...")
        
        # Copy example config
        example_config = Path('config.example.yaml').read_text()
        
        # Try to detect LocalSend path
        home = Path.home()
        localsend_path = home / 'LocalSend'
        
        if localsend_path.exists():
            example_config = example_config.replace(
                'C:/Users/YourName/LocalSend',
                str(localsend_path).replace('\\', '/')
            )
            print(f"   ✅ Found LocalSend at {localsend_path}")
        
        Path('config.yaml').write_text(example_config)
        print("   ✅ Created config.yaml - please update with your settings")
    else:
        print("\n✅ config.yaml already exists")


def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("   ✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install dependencies")
        return False


def main():
    """Run setup process."""
    print("🚀 AI Researcher Setup\n" + "="*40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please fix the requirements above and run setup again.")
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Create config
    create_config()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed. Check errors above.")
        sys.exit(1)
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit config.yaml with your LocalSend paths")
    print("2. Run the minimal test: python tests/test_minimal.py")
    print("3. Try a test assignment: python nightly_run.py")
    print("\nHappy researching! 🔍")


if __name__ == "__main__":
    main()
