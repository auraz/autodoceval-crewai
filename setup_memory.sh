#!/bin/bash
# setup_memory.sh
# Sets up and demonstrates persistent memory capabilities in the CrewAI implementation of AutoDocEval

set -e  # Exit immediately if a command exits with a non-zero status

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXAMPLES_DIR="${SCRIPT_DIR}/examples"
MEMORY_DIR="${HOME}/.crewai"

# Print colored output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}${'='.repeat(80)}${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}${'='.repeat(80)}${NC}"
}

print_step() {
    echo -e "\n${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check if Python is installed
check_dependencies() {
    print_step "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not found. Please install Python 3.9 or newer."
        exit 1
    fi
    
    # Print Python version
    python_version=$(python3 --version)
    print_success "Found $python_version"
    
    # Check if OpenAI API key is set
    if [ -z "${OPENAI_API_KEY}" ]; then
        print_warning "OPENAI_API_KEY environment variable not set"
        echo "Please enter your OpenAI API key: "
        read -r api_key
        export OPENAI_API_KEY="${api_key}"
        print_success "OPENAI_API_KEY set for this session"
    else
        print_success "OPENAI_API_KEY already set"
    fi
}

# Set up virtual environment
setup_venv() {
    print_step "Setting up virtual environment..."
    
    VENV_DIR="${SCRIPT_DIR}/venv"
    if [ ! -d "${VENV_DIR}" ]; then
        python3 -m venv "${VENV_DIR}"
        print_success "Virtual environment created at ${VENV_DIR}"
    else
        print_success "Using existing virtual environment at ${VENV_DIR}"
    fi
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"
    print_success "Virtual environment activated"
    
    # Install requirements
    print_step "Installing required packages..."
    uv pip install -e "${SCRIPT_DIR}"
    print_success "Installed autodoceval-crewai in development mode"
}

# Create sample documents for memory demo
create_samples() {
    print_step "Creating sample documents..."
    
    mkdir -p "${EXAMPLES_DIR}"
    
    # Simple document
    cat > "${EXAMPLES_DIR}/simple_doc.md" << EOF
# Simple API Documentation

This is a basic API document.

## Endpoints

GET /users - Get user list
POST /users - Create user

## Authentication

Use API key in header.
EOF
    
    # More complex document
    cat > "${EXAMPLES_DIR}/complex_doc.md" << EOF
# Advanced API Documentation

This document describes our advanced API features.

## Authentication

All endpoints require authentication with an API key in the header:
\`\`\`
Authorization: Bearer YOUR_API_KEY
\`\`\`

## Rate Limiting

API calls are limited to 100 requests per minute.

## Endpoints

### Users API

- GET /users - Retrieve all users
- GET /users/{id} - Retrieve specific user
- POST /users - Create a new user
- PUT /users/{id} - Update user
- DELETE /users/{id} - Delete user

### Products API

- GET /products - List all products
- POST /products - Create a product
EOF

    print_success "Sample documents created in ${EXAMPLES_DIR}"
}

# Demonstrate memory capabilities
demo_memory() {
    print_header "Demonstrating Memory Capabilities"
    
    MEMORY_ID="autodoceval_demo_memory"
    
    print_step "1. First evaluation with memory ID: ${MEMORY_ID}"
    autodoceval-crewai grade "${EXAMPLES_DIR}/simple_doc.md" --memory-id "${MEMORY_ID}"
    
    print_step "2. Improving document with memory..."
    autodoceval-crewai improve "${EXAMPLES_DIR}/simple_doc.md" --memory-id "${MEMORY_ID}"
    
    echo ""
    print_step "3. Evaluating a different but related document with the same memory ID..."
    echo "This will demonstrate how the evaluator uses knowledge from the previous document"
    echo ""
    autodoceval-crewai grade "${EXAMPLES_DIR}/complex_doc.md" --memory-id "${MEMORY_ID}"
    
    print_step "4. Running an auto-improvement cycle with persistent memory..."
    autodoceval-crewai auto-improve "${EXAMPLES_DIR}/simple_doc.md" --memory-id "${MEMORY_ID}" --iterations 2
}

# Display memory files
show_memory_info() {
    print_header "Memory Storage Information"
    
    if [ -d "${MEMORY_DIR}" ]; then
        print_step "Memory files are stored in: ${MEMORY_DIR}"
        echo "Contents of memory directory:"
        ls -la "${MEMORY_DIR}"
    else
        print_warning "Memory directory not found. It will be created when you first use memory features."
    fi
    
    print_step "Memory structure:"
    echo "- Each memory ID creates a separate memory store"
    echo "- The evaluator and improver agents maintain separate memories"
    echo "- Memory persists between runs and sessions"
}

# Main function
main() {
    print_header "AutoDocEval CrewAI Memory Setup"
    
    check_dependencies
    setup_venv
    create_samples
    demo_memory
    show_memory_info
    
    print_header "Setup Complete"
    echo ""
    echo "You can now use persistent memory with your own documents:"
    echo ""
    echo "1. With CLI:"
    echo "   autodoceval-crewai grade path/to/document.md --memory-id my-memory"
    echo "   autodoceval-crewai improve path/to/document.md --memory-id my-memory"
    echo ""
    echo "2. With Python API:"
    echo "   from autodoceval_crewai import evaluate_document, improve_document"
    echo "   score, feedback = evaluate_document(content, memory_id=\"my-memory\")"
    echo "   improved = improve_document(content, feedback, memory_id=\"my-memory\")"
    echo ""
    echo "For more information, see the MEMORY.md file."
    
    # Deactivate virtual environment
    deactivate
}

# Run the script
main