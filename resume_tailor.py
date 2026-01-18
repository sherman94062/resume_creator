#!/usr/bin/env python3
"""
Resume Tailoring Tool - Uses OpenAI API to tailor resumes to job descriptions
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Check if openai is installed
try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI library not installed. Run: pip install openai")
    sys.exit(1)


class ResumeTailor:
    """Tailors resumes to job descriptions using LLM"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the resume tailor

        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.conversation_history = []

    def log_llm_call(self, role: str, content: str, label: str = ""):
        """Log LLM conversation for visibility"""
        separator = "=" * 80
        print(f"\n{separator}")
        print(f"🤖 LLM CALL {label}")
        print(f"{separator}")
        print(f"Role: {role}")
        print(f"Content:\n{content[:500]}{'...' if len(content) > 500 else ''}")
        print(f"{separator}\n")

    def call_llm(self, prompt: str, system_prompt: Optional[str] = None, label: str = "") -> str:
        """
        Make an LLM API call and log it

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            label: Label for logging

        Returns:
            LLM response text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            self.log_llm_call("system", system_prompt, f"{label} - SYSTEM")

        messages.append({"role": "user", "content": prompt})
        self.log_llm_call("user", prompt, f"{label} - USER")

        print(f"⏳ Calling OpenAI API ({self.model})...")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )

        result = response.choices[0].message.content

        self.log_llm_call("assistant", result, f"{label} - RESPONSE")

        # Log token usage
        print(f"📊 Token Usage:")
        print(f"   Prompt tokens: {response.usage.prompt_tokens}")
        print(f"   Completion tokens: {response.usage.completion_tokens}")
        print(f"   Total tokens: {response.usage.total_tokens}")
        print()

        return result

    def analyze_job_description(self, job_description: str) -> dict:
        """
        Analyze job description to extract key requirements

        Args:
            job_description: The job posting text

        Returns:
            Dictionary with key requirements, skills, keywords
        """
        system_prompt = """You are an expert resume consultant and ATS (Applicant Tracking System) specialist.
Your job is to analyze job descriptions and extract the most important information for resume tailoring."""

        prompt = f"""Analyze this job description and extract:
1. Key responsibilities (top 5-7)
2. Required skills and technologies
3. Important keywords for ATS optimization
4. Desired experience level and background
5. Key performance metrics or success criteria mentioned

Job Description:
{job_description}

Return your analysis in JSON format with keys: responsibilities, skills, keywords, experience_requirements, success_metrics"""

        response = self.call_llm(prompt, system_prompt, label="JOB ANALYSIS")

        # Try to parse JSON from response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except json.JSONDecodeError:
            print("⚠️  Warning: Could not parse JSON response, using raw text")
            return {"raw_analysis": response}

    def tailor_resume(self, original_resume: str, job_description: str, job_analysis: dict) -> str:
        """
        Tailor the resume to the job description

        Args:
            original_resume: Original resume text
            job_description: Job posting text
            job_analysis: Analyzed job requirements

        Returns:
            Tailored resume in markdown format
        """
        system_prompt = """You are an expert resume writer specializing in tailoring resumes for specific job postings.
Your goal is to rewrite resumes to:
1. Highlight the most relevant experience for the target role
2. Use keywords from the job description for ATS optimization
3. Quantify achievements wherever possible
4. Reframe experience to match job requirements
5. Maintain truthfulness - never fabricate experience
6. Create a compelling narrative that shows the candidate is ideal for this role

Return the resume in clean markdown format, well-structured and professional."""

        prompt = f"""Please rewrite this resume to target the following job posting.

JOB DESCRIPTION:
{job_description}

KEY REQUIREMENTS FROM ANALYSIS:
{json.dumps(job_analysis, indent=2)}

ORIGINAL RESUME:
{original_resume}

INSTRUCTIONS:
1. Create a professional summary that speaks directly to this role
2. Reorder and reframe experience sections to emphasize relevant skills
3. Use specific keywords from the job description
4. Add metrics and quantifiable achievements
5. Highlight experience with the technologies/domains mentioned
6. Keep the most relevant experience detailed, summarize less relevant roles
7. Ensure ATS compatibility
8. Format in clean markdown with clear sections

Return ONLY the tailored resume in markdown format, starting with the name and contact info."""

        return self.call_llm(prompt, system_prompt, label="RESUME TAILORING")

    def generate_pdf(self, markdown_content: str, output_path: str):
        """
        Convert markdown resume to professional PDF

        Args:
            markdown_content: Resume in markdown format
            output_path: Path to save PDF
        """
        print(f"📄 Generating PDF: {output_path}")

        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content, extensions=['extra', 'nl2br'])

        # Professional resume CSS
        css_content = """
        @page {
            size: letter;
            margin: 0.5in;
        }

        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #202020;
            max-width: 100%;
        }

        h1 {
            font-size: 24pt;
            font-weight: bold;
            margin: 0 0 5pt 0;
            padding: 0;
            color: #1a1a1a;
            letter-spacing: 0.5pt;
        }

        h2 {
            font-size: 13pt;
            font-weight: bold;
            margin: 16pt 0 8pt 0;
            padding-bottom: 4pt;
            border-bottom: 2pt solid #2c5aa0;
            color: #2c5aa0;
            text-transform: uppercase;
            letter-spacing: 0.5pt;
        }

        h3 {
            font-size: 11pt;
            font-weight: bold;
            margin: 10pt 0 4pt 0;
            color: #1a1a1a;
        }

        h4 {
            font-size: 10pt;
            font-weight: bold;
            font-style: italic;
            margin: 6pt 0 4pt 0;
            color: #404040;
        }

        p {
            margin: 0 0 8pt 0;
            text-align: justify;
        }

        ul {
            margin: 4pt 0 8pt 0;
            padding-left: 18pt;
        }

        li {
            margin: 3pt 0;
        }

        strong {
            font-weight: bold;
            color: #1a1a1a;
        }

        em {
            font-style: italic;
            color: #404040;
        }

        hr {
            border: none;
            border-top: 1pt solid #cccccc;
            margin: 10pt 0;
        }

        body > p:first-of-type {
            text-align: center;
            font-size: 9pt;
            color: #404040;
            margin: 0 0 10pt 0;
        }

        h2:first-of-type + p {
            background-color: #f5f5f5;
            padding: 10pt;
            border-left: 3pt solid #2c5aa0;
            margin-bottom: 10pt;
        }

        h3 + p {
            margin-bottom: 4pt;
        }

        h4 + p {
            margin-bottom: 6pt;
        }

        ul li strong:first-child {
            color: #2c5aa0;
        }

        h2, h3, h4 {
            page-break-after: avoid;
        }

        li {
            page-break-inside: avoid;
        }

        a {
            color: #2c5aa0;
            text-decoration: none;
        }
        """

        # Create full HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Tailored Resume</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Configure fonts and generate PDF
        font_config = FontConfiguration()
        HTML(string=full_html).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_content, font_config=font_config)],
            font_config=font_config
        )

        print(f"✓ PDF generated successfully: {output_path}")

    def tailor_resume_workflow(self,
                               resume_path: str,
                               job_desc_path: str,
                               output_basename: str = "tailored_resume") -> dict:
        """
        Complete workflow to tailor a resume

        Args:
            resume_path: Path to original resume file
            job_desc_path: Path to job description file (or text string)
            output_basename: Base name for output files

        Returns:
            Dictionary with paths to generated files
        """
        print("🚀 Starting Resume Tailoring Workflow")
        print("=" * 80)

        # Read inputs
        print(f"📖 Reading original resume: {resume_path}")
        with open(resume_path, 'r') as f:
            original_resume = f.read()

        # Job description can be a file or direct text
        if os.path.exists(job_desc_path):
            print(f"📖 Reading job description: {job_desc_path}")
            with open(job_desc_path, 'r') as f:
                job_description = f.read()
        else:
            print(f"📖 Using job description from text")
            job_description = job_desc_path

        # Step 1: Analyze job description
        print("\n📊 STEP 1: Analyzing job description...")
        job_analysis = self.analyze_job_description(job_description)

        # Save analysis
        analysis_path = f"{output_basename}_analysis.json"
        with open(analysis_path, 'w') as f:
            json.dump(job_analysis, f, indent=2)
        print(f"✓ Job analysis saved: {analysis_path}")

        # Step 2: Tailor resume
        print("\n✍️  STEP 2: Tailoring resume to job requirements...")
        tailored_resume = self.tailor_resume(original_resume, job_description, job_analysis)

        # Save markdown version
        md_path = f"{output_basename}.md"
        with open(md_path, 'w') as f:
            f.write(tailored_resume)
        print(f"✓ Tailored resume (markdown) saved: {md_path}")

        # Step 3: Generate PDF
        print("\n📄 STEP 3: Generating PDF...")
        pdf_path = f"{output_basename}.pdf"
        self.generate_pdf(tailored_resume, pdf_path)

        print("\n" + "=" * 80)
        print("✅ Resume Tailoring Complete!")
        print("=" * 80)

        return {
            "analysis": analysis_path,
            "markdown": md_path,
            "pdf": pdf_path
        }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Tailor a resume to a specific job description using AI"
    )
    parser.add_argument(
        "resume",
        help="Path to original resume file"
    )
    parser.add_argument(
        "job_description",
        help="Path to job description file or direct text"
    )
    parser.add_argument(
        "-o", "--output",
        default="tailored_resume",
        help="Base name for output files (default: tailored_resume)"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )

    args = parser.parse_args()

    try:
        # Initialize tailor
        tailor = ResumeTailor(api_key=args.api_key, model=args.model)

        # Run workflow
        results = tailor.tailor_resume_workflow(
            resume_path=args.resume,
            job_desc_path=args.job_description,
            output_basename=args.output
        )

        print("\n📁 Generated Files:")
        for file_type, path in results.items():
            print(f"   {file_type}: {path}")

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
