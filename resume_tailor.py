import os
import argparse
import json
import markdown
from typing import Optional
from openai import OpenAI
from pypdf import PdfReader
from weasyprint import HTML, CSS
from models import JobAnalysis, ReflectionCritique

class ResumeTailor:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize with API key and selected model.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def read_pdf(self, file_path: str) -> str:
        """Extracts text from a PDF file for LLM processing."""
        print(f"📖 Reading PDF: {file_path}")
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            raise

    def call_llm_structured(self, prompt: str, system_prompt: str, response_format):
        """Helper to call LLM with Structured Outputs. Temperature is set to 0 for consistency."""
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format=response_format,
            temperature=0.0  # Zero temperature for consistent Match Scores and analysis
        )
        return response.choices[0].message.parsed

    def analyze_job_description(self, jd_text: str) -> JobAnalysis:
        """Step 1: Extract key requirements using Structured Outputs."""
        system_prompt = "You are an expert ATS specialist. Extract key requirements from job descriptions."
        prompt = f"Analyze this job description and extract the key details:\n\n{jd_text}"
        return self.call_llm_structured(prompt, system_prompt, JobAnalysis)

    def reflect_on_resume(self, tailored_resume: str, jd_text: str) -> ReflectionCritique:
        """Step 3: Critique the generated resume for quality and accuracy."""
        system_prompt = """You are a critical hiring manager and ATS specialist.
        Evaluate if this resume matches the job requirements.

        Consider:
        - Does it include the required skills and experience?
        - Are relevant keywords from the job description present?
        - Are achievements quantified with metrics?
        - Is the experience framed to match the job requirements?
        - What specific gaps remain between the resume and job requirements?"""

        prompt = f"""JOB DESCRIPTION:
{jd_text}

TAILORED RESUME:
{tailored_resume}

Evaluate this resume against the job description. Provide a match score (0-100) and specific critique points about what's missing or weak."""
        return self.call_llm_structured(prompt, system_prompt, ReflectionCritique)
    
    def generate_pdf(self, markdown_content: str, output_path: str):
        """Step 4: Convert Markdown to a polished executive PDF."""
        print(f"📄 Generating PDF: {output_path}")
        html_content = markdown.markdown(markdown_content, extensions=['extra', 'nl2br'])
        
        # Professional executive-style CSS for a clean, non-ugly layout
        css = CSS(string="""
            @page { 
                size: letter; 
                margin: 0.5in 0.65in; 
                @bottom-right {
                    content: counter(page);
                    font-size: 9pt;
                    color: #999;
                }
            }
            body { 
                font-family: 'Helvetica', 'Arial', sans-serif; 
                font-size: 10pt; 
                line-height: 1.4; 
                color: #333; 
            }
            h1 { 
                font-size: 24pt; 
                color: #1a1a1a; 
                margin-bottom: 2pt; 
                text-align: center; 
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 300;
            }
            /* Contact Line */
            h1 + p { 
                text-align: center; 
                font-size: 8.5pt; 
                color: #555; 
                margin-bottom: 25pt; 
                text-transform: uppercase;
                letter-spacing: 1px;
                border-bottom: 1px solid #eee;
                padding-bottom: 10pt;
            }
            h2 { 
                font-size: 12pt; 
                color: #2c5aa0; 
                border-bottom: 1.5pt solid #2c5aa0; 
                text-transform: uppercase; 
                margin-top: 20pt; 
                margin-bottom: 10pt; 
                font-weight: bold; 
                letter-spacing: 1px;
            }
            h3 { 
                font-size: 11pt; 
                font-weight: bold; 
                margin-top: 12pt; 
                margin-bottom: 0; 
                color: #1a1a1a;
            }
            /* Date and Location line */
            h3 + p { 
                font-style: italic; 
                color: #4a5568; 
                font-size: 9pt; 
                margin-top: 0;
                margin-bottom: 6pt; 
            }
            ul { 
                margin-top: 0; 
                margin-bottom: 8pt; 
                padding-left: 15pt; 
            }
            li { 
                margin-bottom: 3pt; 
                text-align: justify;
            }
            strong { 
                color: #2d3748; 
                font-weight: 600; 
            }
        """)
        
        full_html = f"<!DOCTYPE html><html><body>{html_content}</body></html>"
        HTML(string=full_html).write_pdf(output_path, stylesheets=[css])

    def tailor_resume(self, original: str, jd: str, analysis: JobAnalysis, critique_points: str = "") -> str:
        """Step 2: Synthesize the tailored resume text with proper hierarchy."""
        system_prompt = """You are an expert technical resume writer.
        Format headers strictly: # for Name, ## for Sections, ### for Role/Company.
        Ensure a separate line for Dates/Location immediately under ### headers.

        CRITICAL RULES:
        - Use ONLY information from the ORIGINAL RESUME DATA provided
        - DO NOT add, fabricate, or hallucinate any experience, skills, or achievements
        - DO NOT omit relevant experience from the original resume
        - Reframe and reorganize existing content to match job requirements
        - Use keywords from the job description where they naturally fit existing experience"""

        refinement_instr = f"\n\nREVISION FOCUS:\n{critique_points}" if critique_points else ""

        prompt = f"""
        ORIGINAL RESUME DATA:
        {original}

        TARGET JOB REQUIREMENTS:
        {analysis.model_dump_json(indent=2)}

        {refinement_instr}

        Rewrite this resume in clean Markdown format to match the target job requirements:

        1. Emphasize experience and skills that align with the job requirements
        2. Reorganize bullet points to highlight most relevant achievements first
        3. Use keywords from the job description naturally throughout
        4. Quantify accomplishments with metrics wherever they exist
        5. Reframe technical experience to match the job's domain and terminology

        Remember: Use ONLY content from the original resume. Do not add fictional experience.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content

    def run_workflow(self, resume_path: str, jd_path: str, output_name: str = "tailored_resume.pdf"):
        """Orchestrate the process and track the best version to prevent score regression."""
        if resume_path.lower().endswith('.pdf'):
            original = self.read_pdf(resume_path)
        else:
            with open(resume_path, 'r') as f: original = f.read()

        with open(jd_path, 'r') as f: jd = f.read()

        # Step 1: Analysis
        print("🔍 Analyzing Job Description...")
        analysis = self.analyze_job_description(jd)

        # Step 2: Initial Draft
        print("✍️  Generating Initial Draft...")
        current_resume = self.tailor_resume(original, jd, analysis)
        
        # Track the best version found so far
        best_resume = current_resume
        best_score = -1

        # Step 3: Reflection & Refinement Loop
        for i in range(2):
            print(f"🧐 Reflection Attempt {i+1}...")
            critique = self.reflect_on_resume(current_resume, jd)
            print(f"   Match Score: {critique.match_score}/100")

            # Update best version if current score is higher
            if critique.match_score > best_score:
                best_score = critique.match_score
                best_resume = current_resume
                print(f"   ⭐ New best version tracked!")

            # Check if score is below 70% threshold
            if critique.match_score < 70:
                print(f"\n⚠️  WARNING: Match score ({critique.match_score}%) is below 70%")
                print("\n📋 Areas that need improvement:")
                for idx, point in enumerate(critique.critique_points, 1):
                    print(f"   {idx}. {point}")

                print("\n💡 Your original resume may be missing key experience or skills for this role.")
                print("   Consider updating your master resume to include:")
                print("   - More relevant technical skills or certifications")
                print("   - Experience with required tools/platforms")
                print("   - Quantifiable achievements in areas mentioned in the job description")

                response = input("\n❓ Continue with current resume (c) or stop to update resume (s)? [c/s]: ").strip().lower()

                if response == 's' or response == 'stop':
                    print("\n🛑 Stopping to allow resume updates.")
                    print(f"   Current best score: {best_score}/100")
                    print(f"\n   After updating your resume, run the tool again with:")
                    print(f"   python resume_tailor.py <updated_resume> {jd_path} -o {output_name}")
                    return None
                else:
                    print("\n▶️  Continuing with current resume...\n")

            if critique.needs_revision and i < 1:
                print(f"   🔄 Refining based on critique points...")
                current_resume = self.tailor_resume(original, jd, analysis, ". ".join(critique.critique_points))
            else:
                if not critique.needs_revision:
                    print("   ✅ Quality check passed!")
                break

        # Final Step: Generate PDF from the version with the highest Match Score
        print(f"🏆 Finalizing PDF with Best Score: {best_score}/100")
        self.generate_pdf(best_resume, output_name)
        return best_resume

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tailor a resume with Executive PDF support")
    parser.add_argument("resume", help="Path to original resume (.pdf or .txt)")
    parser.add_argument("job", help="Path to job description (.txt)")
    parser.add_argument("-o", "--output", default="tailored_resume.pdf", help="Output PDF name")
    
    args = parser.parse_args()

    try:
        tailor = ResumeTailor()
        result = tailor.run_workflow(args.resume, args.job, args.output)
        if result is not None:
            print(f"\n✨ Successfully created: {args.output}")
        else:
            print("\n👋 Exiting. Good luck with your resume updates!")
    except Exception as e:
        print(f"\n❌ Error: {e}")