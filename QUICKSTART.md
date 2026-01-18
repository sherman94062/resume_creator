# Quick Start Guide

Get your tailored resume in 5 minutes!

## Prerequisites

You need an OpenAI API key. Get one at: https://platform.openai.com/api-keys

## Installation (One-Time Setup)

```bash
# 1. Navigate to the resume_creator directory
cd /Users/arthursherman/resume_creator

# 2. Activate the virtual environment (already created)
source venv/bin/activate

# 3. Install the OpenAI library
pip install openai

# Verify everything is installed
pip list | grep -E "openai|markdown|weasyprint"
```

## Usage - Option 1: Command Line

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Run the tool
python resume_tailor.py \
  original_resume.txt \
  job_description_qa_csm.txt \
  -o My_Tailored_Resume

# This will generate:
# - My_Tailored_Resume_analysis.json (job analysis)
# - My_Tailored_Resume.md (markdown resume)
# - My_Tailored_Resume.pdf (formatted PDF)
```

## Usage - Option 2: Python Script

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Run the example script
python example_usage.py
```

## Usage - Option 3: Interactive Python

```python
from resume_tailor import ResumeTailor

# Initialize
tailor = ResumeTailor(api_key="sk-your-api-key-here")

# Tailor resume
results = tailor.tailor_resume_workflow(
    resume_path="original_resume.txt",
    job_desc_path="job_description_qa_csm.txt",
    output_basename="tailored_resume"
)

print(results)
```

## What You'll See

The tool provides **full transparency** - you'll see:

1. **System Prompt** - Instructions given to the AI
2. **User Prompt** - Your resume and job description
3. **AI Response** - The tailored resume
4. **Token Usage** - Cost breakdown

Example output:
```
================================================================================
🤖 LLM CALL JOB ANALYSIS - SYSTEM
================================================================================
Role: system
Content: You are an expert resume consultant and ATS specialist...
================================================================================

⏳ Calling OpenAI API (gpt-4o)...

📊 Token Usage:
   Prompt tokens: 1,234
   Completion tokens: 567
   Total tokens: 1,801
```

## Cost Estimate

Using **GPT-4o** (recommended):
- ~$0.05-$0.06 per resume

Using **GPT-3.5-turbo** (cheaper):
```bash
python resume_tailor.py original_resume.txt job_desc.txt -m gpt-3.5-turbo
```
- ~$0.01 per resume

## Test It Now!

Sample files are already included:
- `original_resume.txt` - Your original resume
- `job_description_qa_csm.txt` - QA CSM job posting

Just run:
```bash
source venv/bin/activate
export OPENAI_API_KEY="sk-..."
python resume_tailor.py original_resume.txt job_description_qa_csm.txt -o test_output
```

## Troubleshooting

### "No module named 'openai'"
```bash
source venv/bin/activate
pip install openai
```

### "OpenAI API key required"
```bash
export OPENAI_API_KEY="sk-..."
# Or pass directly: -k sk-...
```

### "cannot load library 'libpango'"
The system libraries are already installed. If you get this error, try:
```bash
brew reinstall pango cairo gdk-pixbuf
```

### PDF looks weird
The PDF uses standard fonts (Helvetica/Arial). If you see issues:
1. Check the markdown file first - it has the same content
2. Customize the CSS in `resume_tailor.py` (line 220+)

## Next Steps

1. **Review the output** - Check `*_analysis.json` to see what the AI extracted
2. **Read the markdown** - Easier to edit than PDF
3. **Customize prompts** - Edit `resume_tailor.py` to adjust the AI instructions
4. **Try different jobs** - Create new job description files and run again

## Support

Questions? Check:
- `README.md` - Full documentation
- `resume_tailor.py` - Source code with comments
- `example_usage.py` - Usage examples

Enjoy tailoring your resume! 🎯
