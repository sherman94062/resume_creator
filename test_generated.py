import pytest
from unittest.mock import Mock, patch

# Tests for models.py
import pytest
from models import JobAnalysis, ReflectionCritique
from pydantic import ValidationError

@pytest.fixture
def valid_job_analysis():
    return JobAnalysis(
        responsibilities=["Develop software", "Test applications", "Collaborate with team", "Document processes", "Maintain systems"],
        skills=["Python", "Django", "JavaScript"],
        keywords=["software development", "agile", "teamwork"],
        experience_requirements="3-5 years",
        success_metrics=["Increased efficiency by 20%", "Reduced bugs by 30%"]
    )

@pytest.fixture
def valid_reflection_critique():
    return ReflectionCritique(
        match_score=85,
        critique_points=["Missing specific technologies", "Needs more quantifiable achievements"],
        hallucination_check=False,
        needs_revision=True
    )

def test_job_analysis_creation(valid_job_analysis):
    """Test successful creation of JobAnalysis instance."""
    assert valid_job_analysis.responsibilities == ["Develop software", "Test applications", "Collaborate with team", "Document processes", "Maintain systems"]
    assert valid_job_analysis.skills == ["Python", "Django", "JavaScript"]
    assert valid_job_analysis.keywords == ["software development", "agile", "teamwork"]
    assert valid_job_analysis.experience_requirements == "3-5 years"
    assert valid_job_analysis.success_metrics == ["Increased efficiency by 20%", "Reduced bugs by 30%"]

def test_job_analysis_empty_fields():
    """Test creation of JobAnalysis with empty fields."""
    job_analysis = JobAnalysis(
        responsibilities=[],
        skills=[],
        keywords=[],
        experience_requirements="",
        success_metrics=[]
    )
    assert job_analysis.responsibilities == []
    assert job_analysis.skills == []
    assert job_analysis.keywords == []
    assert job_analysis.experience_requirements == ""
    assert job_analysis.success_metrics == []

def test_job_analysis_invalid_experience_requirements():
    """Test JobAnalysis raises ValidationError for invalid experience requirements."""
    with pytest.raises(ValidationError):
        JobAnalysis(
            responsibilities=["Develop software"],
            skills=["Python"],
            keywords=["software development"],
            experience_requirements=123,  # Invalid type
            success_metrics=["Increased efficiency by 20%"]
        )

def test_reflection_critique_creation(valid_reflection_critique):
    """Test successful creation of ReflectionCritique instance."""
    assert valid_reflection_critique.match_score == 85
    assert valid_reflection_critique.critique_points == ["Missing specific technologies", "Needs more quantifiable achievements"]
    assert valid_reflection_critique.hallucination_check is False
    assert valid_reflection_critique.needs_revision is True

def test_reflection_critique_invalid_match_score():
    """Test ReflectionCritique raises ValidationError for invalid match score."""
    with pytest.raises(ValidationError):
        ReflectionCritique(
            match_score=110,  # Out of valid range
            critique_points=["Missing specific technologies"],
            hallucination_check=False,
            needs_revision=True
        )

def test_reflection_critique_empty_fields():
    """Test creation of ReflectionCritique with empty fields."""
    reflection_critique = ReflectionCritique(
        match_score=0,
        critique_points=[],
        hallucination_check=False,
        needs_revision=False
    )
    assert reflection_critique.match_score == 0
    assert reflection_critique.critique_points == []
    assert reflection_critique.hallucination_check is False
    assert reflection_critique.needs_revision is False

# Tests for resume_tailor.py
import pytest
from unittest.mock import patch, MagicMock
from resume_tailor import ResumeTailor
from models import JobAnalysis, ReflectionCritique

@pytest.fixture
def resume_tailor_instance():
    with patch('resume_tailor.OpenAI') as mock_openai:
        instance = ResumeTailor(api_key="test_api_key")
        yield instance

def test_read_pdf_valid(resume_tailor_instance, tmp_path):
    """Test reading a valid PDF file."""
    pdf_content = "This is a test PDF content."
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text(pdf_content)

    with patch('resume_tailor.PdfReader') as mock_pdf_reader:
        mock_pdf_reader.return_value.pages = [MagicMock(extract_text=MagicMock(return_value=pdf_content))]
        result = resume_tailor_instance.read_pdf(str(pdf_file))
        assert result == pdf_content + "\n"

def test_read_pdf_invalid(resume_tailor_instance):
    """Test reading an invalid PDF file raises an exception."""
    with patch('resume_tailor.PdfReader', side_effect=Exception("File not found")):
        with pytest.raises(Exception, match="Error reading PDF: File not found"):
            resume_tailor_instance.read_pdf("invalid.pdf")

def test_call_llm_structured(resume_tailor_instance):
    """Test calling LLM with structured output."""
    prompt = "Test prompt"
    system_prompt = "Test system prompt"
    response_format = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.parsed = "parsed_response"

    with patch.object(resume_tailor_instance.client.beta.chat.completions, 'parse', return_value=mock_response):
        result = resume_tailor_instance.call_llm_structured(prompt, system_prompt, response_format)
        assert result == "parsed_response"

def test_analyze_job_description(resume_tailor_instance):
    """Test analyzing job description."""
    jd_text = "Job description text."
    mock_job_analysis = JobAnalysis(responsibilities=[], skills=[], keywords=[], experience_requirements="", success_metrics=[])

    with patch.object(resume_tailor_instance, 'call_llm_structured', return_value=mock_job_analysis):
        result = resume_tailor_instance.analyze_job_description(jd_text)
        assert result == mock_job_analysis

def test_reflect_on_resume(resume_tailor_instance):
    """Test reflecting on resume."""
    tailored_resume = "Tailored resume text."
    jd_text = "Job description text."
    mock_reflection_critique = ReflectionCritique(match_score=85, critique_points=["Point 1"], hallucination_check=False, needs_revision=False)

    with patch.object(resume_tailor_instance, 'call_llm_structured', return_value=mock_reflection_critique):
        result = resume_tailor_instance.reflect_on_resume(tailored_resume, jd_text)
        assert result == mock_reflection_critique

def test_generate_pdf(resume_tailor_instance, tmp_path):
    """Test generating a PDF from markdown content."""
    markdown_content = "# Test Resume"
    output_path = tmp_path / "output.pdf"

    with patch('resume_tailor.HTML.write_pdf') as mock_write_pdf:
        resume_tailor_instance.generate_pdf(markdown_content, str(output_path))
        mock_write_pdf.assert_called_once()

def test_tailor_resume(resume_tailor_instance):
    """Test tailoring the resume."""
    original = "Original resume content."
    jd = "Job description text."
    mock_analysis = JobAnalysis(responsibilities=[], skills=[], keywords=[], experience_requirements="", success_metrics=[])
    critique_points = "Critique points."

    with patch.object(resume_tailor_instance.client.chat.completions, 'create', return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="Tailored resume content."))])):
        result = resume_tailor_instance.tailor_resume(original, jd, mock_analysis, critique_points)
        assert result == "Tailored resume content."

def test_run_workflow(resume_tailor_instance, tmp_path):
    """Test running the entire workflow."""
    resume_path = tmp_path / "resume.txt"
    resume_path.write_text("Original resume content.")
    jd_path = tmp_path / "job_description.txt"
    jd_path.write_text("Job description text.")

    with patch.object(resume_tailor_instance, 'read_pdf', return_value="Original resume content."), \
         patch.object(resume_tailor_instance, 'analyze_job_description', return_value=JobAnalysis(responsibilities=[], skills=[], keywords=[], experience_requirements="", success_metrics=[])), \
         patch.object(resume_tailor_instance, 'tailor_resume', return_value="Tailored resume content."), \
         patch.object(resume_tailor_instance, 'reflect_on_resume', return_value=ReflectionCritique(match_score=85, critique_points=[], hallucination_check=False, needs_revision=False)), \
         patch.object(resume_tailor_instance, 'generate_pdf') as mock_generate_pdf:
        
        result = resume_tailor_instance.run_workflow(str(resume_path), str(jd_path))
        assert result == "Tailored resume content."
        mock_generate_pdf.assert_called_once()

# Tests for example_usage.py
import os
from unittest.mock import patch, MagicMock
import pytest
from example_usage import main

@patch('example_usage.os.getenv', return_value=None)
def test_main_missing_api_key(mock_getenv):
    """Test main function when OPENAI_API_KEY is not set."""
    with patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("❌ Error: Please set OPENAI_API_KEY environment variable")
        mock_print.assert_any_call("   export OPENAI_API_KEY='sk-...'")

@patch('example_usage.os.getenv', return_value='sk-123456')
@patch('example_usage.os.path.exists', side_effect=lambda x: False)
def test_main_file_not_found(mock_exists, mock_getenv):
    """Test main function when required files do not exist."""
    with patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("❌ Error: original_resume.txt not found")
        mock_print.assert_any_call("   Please create this file with your resume content")
        
        mock_print.assert_any_call("❌ Error: job_description_qa_csm.txt not found")
        mock_print.assert_any_call("   Please create this file with the job description")

@patch('example_usage.os.getenv', return_value='sk-123456')
@patch('example_usage.os.path.exists', side_effect=lambda x: True)
@patch('example_usage.ResumeTailor')
@patch('example_usage.os.path.getsize', return_value=2048)
def test_main_success(mock_getsize, mock_ResumeTailor, mock_exists, mock_getenv):
    """Test main function when everything is set up correctly."""
    mock_tailor_instance = MagicMock()
    mock_tailor_instance.tailor_resume_workflow.return_value = {
        'pdf': 'output.pdf',
        'json': 'output.json',
        'markdown': 'output.md'
    }
    mock_ResumeTailor.return_value = mock_tailor_instance
    
    with patch('builtins.print') as mock_print:
        main()
        
        mock_print.assert_any_call("Resume Tailoring Tool - Example Usage")
        mock_print.assert_any_call("🔧 Initializing Resume Tailor with GPT-4o...")
        mock_print.assert_any_call("🚀 Tailoring resume for job posting...")
        mock_print.assert_any_call("   Resume: original_resume.txt")
        mock_print.assert_any_call("   Job Description: job_description_qa_csm.txt")
        mock_print.assert_any_call("   Output: example_tailored_resume.*")
        mock_print.assert_any_call("✅ SUCCESS! Generated files:")
        mock_print.assert_any_call("   📄 PDF: output.pdf (2.0 KB)")
        mock_print.assert_any_call("   📄 JSON: output.json (2.0 KB)")
        mock_print.assert_any_call("   📄 MARKDOWN: output.md (2.0 KB)")
