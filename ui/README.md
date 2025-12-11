# Web UI for Hybrid LLM Vulnerability Repair Framework

A modern web-based user interface built with Streamlit for the Hybrid LLM Vulnerability Repair Framework.

## Features

- 🎨 Modern, intuitive web interface
- 📝 Code input via paste or file upload
- 📊 Real-time analysis and results visualization
- 📥 Download fixed code and results
- ⚙️ Configurable settings (refinement, verification)
- 📈 Detailed metrics and statistics

## Installation

Install Streamlit (if not already installed):

```bash
pip install streamlit
```

Or install from UI requirements:

```bash
pip install -r ui/requirements.txt
```

## Usage

### Start the Web UI

```bash
streamlit run ui/app.py
```

The UI will open in your default web browser at `http://localhost:8501`

### Using the UI

1. **Code Analysis Tab**:
   - Choose to paste code or upload a file
   - Select programming language
   - Click "Analyze & Repair"
   - Wait for analysis to complete

2. **Results & Metrics Tab**:
   - View detected vulnerabilities
   - See fixed code for each vulnerability
   - Check metrics (similarity, quality, verification status)
   - Download fixed code or results

3. **Documentation Tab**:
   - Read framework overview
   - Learn about features and supported languages

## Features

### Input Methods
- **Paste Code**: Directly paste code into text area
- **Upload File**: Upload source code files (.py, .cpp, .c, .java)

### Configuration
- Enable/disable multi-iteration refinement
- Enable/disable exploit-based verification
- View model availability status

### Results Display
- Summary metrics (vulnerabilities found, success rate, processing time)
- Detailed vulnerability information (CWE, severity, line number)
- Fixed code with syntax highlighting
- Quality metrics (similarity, fix quality, verification status)
- Download options for fixed code and results

## Screenshots

The UI provides:
- Clean, modern interface
- Real-time progress indicators
- Expandable vulnerability details
- Code syntax highlighting
- Export functionality

## Troubleshooting

### UI doesn't start
- Ensure Streamlit is installed: `pip install streamlit`
- Check if port 8501 is available
- Try: `streamlit run ui/app.py --server.port 8502`

### Models not available
- Check CodeLlama: Ensure Ollama is running (`ollama serve`)
- Check ChatGPT: Verify `OPENAI_API_KEY` is set

### Code processing fails
- Check that code is valid syntax
- Ensure language is correctly selected
- Check console for error messages

## Development

To modify the UI:

1. Edit `ui/app.py`
2. Restart Streamlit: `streamlit run ui/app.py`
3. Changes will auto-reload

## Integration

The UI uses the same framework backend (`src/main.py`), so all CLI functionality is available through the web interface.

