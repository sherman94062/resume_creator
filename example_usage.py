#!/usr/bin/env python3
"""
Example usage of the Resume Tailoring Tool
"""

import os
from resume_tailor import ResumeTailor

def main():
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='sk-...'")
        return

    print("Resume Tailoring Tool - Example Usage")
    print("=" * 80)

    # Initialize the tailor
    print("🔧 Initializing Resume Tailor with GPT-4o...")
    tailor = ResumeTailor(api_key=api_key, model="gpt-4o")

    # Define file paths
    original_resume = "original_resume.txt"
    job_description = "job_description_qa_csm.txt"
    output_name = "example_tailored_resume"

    # Check if files exist
    if not os.path.exists(original_resume):
        print(f"❌ Error: {original_resume} not found")
        print("   Please create this file with your resume content")
        return

    if not os.path.exists(job_description):
        print(f"❌ Error: {job_description} not found")
        print("   Please create this file with the job description")
        return

    # Run the tailoring workflow
    print(f"\n🚀 Tailoring resume for job posting...")
    print(f"   Resume: {original_resume}")
    print(f"   Job Description: {job_description}")
    print(f"   Output: {output_name}.*")

    results = tailor.tailor_resume_workflow(
        resume_path=original_resume,
        job_desc_path=job_description,
        output_basename=output_name
    )

    # Display results
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Generated files:")
    print("=" * 80)
    for file_type, path in results.items():
        file_size = os.path.getsize(path) / 1024  # KB
        print(f"   📄 {file_type.upper()}: {path} ({file_size:.1f} KB)")

    print("\n💡 Next steps:")
    print("   1. Review the analysis JSON to see what the LLM extracted")
    print("   2. Read the markdown version to check the content")
    print("   3. Open the PDF to see the final formatted resume")
    print("   4. Customize and refine as needed!")


if __name__ == "__main__":
    main()
