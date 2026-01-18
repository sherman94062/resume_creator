# Resume Tailoring Tool

Automatically tailor your resume to specific job descriptions using AI (OpenAI GPT).

## Features

- 📊 Analyzes job descriptions to extract key requirements
- ✍️ Rewrites resume to emphasize relevant experience
- 🎯 Optimizes for ATS (Applicant Tracking Systems)
- 📄 Generates professional PDF output
- 👀 Shows all LLM API calls for transparency
- 💾 Saves job analysis in JSON format

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install system dependencies (macOS with Homebrew):
```bash
brew install pango cairo gdk-pixbuf
```

For other operating systems, see: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html

## Usage

### Command Line

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Tailor your resume
python resume_tailor.py original_resume.txt job_description.txt -o output_name

# Or pass API key directly
python resume_tailor.py original_resume.txt job_description.txt -k sk-... -o output_name
```

### Python Script

```python
from resume_tailor import ResumeTailor

# Initialize with your API key
tailor = ResumeTailor(api_key="sk-...", model="gpt-4o")

# Run the workflow
results = tailor.tailor_resume_workflow(
    resume_path="original_resume.txt",
    job_desc_path="job_description.txt",
    output_basename="tailored_resume"
)

print(f"Generated files: {results}")
```

### Options

- `-o, --output`: Base name for output files (default: `tailored_resume`)
- `-k, --api-key`: OpenAI API key (or use `OPENAI_API_KEY` env var)
- `-m, --model`: OpenAI model to use (default: `gpt-4o`)

## Output Files

The tool generates three files:

1. **`{output}_analysis.json`** - Structured analysis of job requirements
2. **`{output}.md`** - Tailored resume in Markdown format
3. **`{output}.pdf`** - Professional PDF resume

## How It Works

1. **Job Analysis**: LLM analyzes the job description to extract:
   - Key responsibilities
   - Required skills and technologies
   - ATS keywords
   - Experience requirements
   - Success metrics

2. **Resume Tailoring**: LLM rewrites the resume to:
   - Highlight relevant experience
   - Use job-specific keywords
   - Emphasize matching skills
   - Quantify achievements
   - Optimize section ordering

3. **PDF Generation**: Creates a professionally formatted PDF with:
   - Clean, ATS-friendly layout
   - Proper typography and spacing
   - Highlighted sections and metrics

## Transparency

All LLM API calls are logged to the console, showing:
- System prompts
- User prompts
- LLM responses
- Token usage

This allows you to see exactly what data is sent to OpenAI and what responses are received.

## Cost Estimation

Using GPT-4o:
- Job analysis: ~1,500-2,000 tokens ($0.015-$0.020)
- Resume tailoring: ~3,000-4,000 tokens ($0.030-$0.040)
- **Total per resume: ~$0.05-$0.06**

Using GPT-3.5-turbo (cheaper, lower quality):
- **Total per resume: ~$0.01**

## Privacy & Security

- Resume data is sent to OpenAI's API for processing
- No data is stored by this tool except output files
- Consider OpenAI's data usage policies for sensitive information
- Use organization API keys with data retention policies if needed

## Models Supported

- `gpt-4o` (default) - Best quality
- `gpt-4-turbo` - Fast and capable
- `gpt-3.5-turbo` - Cheapest option
- `gpt-4` - Original GPT-4 (slower, more expensive)

## Example

```bash
# Using the example from this project
source venv/bin/activate
export OPENAI_API_KEY="sk-..."

python resume_tailor.py \
  original_resume.txt \
  job_description_qa_csm.txt \
  -o Arthur_Sherman_QA_CSM \
  -m gpt-4o
```

This will generate:
- `Arthur_Sherman_QA_CSM_analysis.json`
- `Arthur_Sherman_QA_CSM.md`
- `Arthur_Sherman_QA_CSM.pdf`

## Limitations

- Requires internet connection for OpenAI API
- Quality depends on LLM model used
- Does not fabricate experience (maintains truthfulness)
- Best results with detailed original resumes
- PDF generation requires system libraries (pango, cairo)

## License

MIT License - feel free to modify and use for personal or commercial purposes.
