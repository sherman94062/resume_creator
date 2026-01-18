#!/usr/bin/env python3
"""
Convert markdown resume to a professionally formatted PDF
"""

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Read the markdown file
with open('Arthur_Sherman_Resume_QA_CSM.md', 'r') as f:
    md_content = f.read()

# Convert markdown to HTML
html_content = markdown.markdown(md_content, extensions=['extra', 'nl2br'])

# Professional resume CSS styling
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

/* Contact info styling */
body > p:first-of-type {
    text-align: center;
    font-size: 9pt;
    color: #404040;
    margin: 0 0 10pt 0;
}

/* Professional summary box */
h2:first-of-type + p {
    background-color: #f5f5f5;
    padding: 10pt;
    border-left: 3pt solid #2c5aa0;
    margin-bottom: 10pt;
}

/* Core competencies styling */
h2 + p strong {
    display: block;
    margin-bottom: 4pt;
}

/* Tighten spacing for experience sections */
h3 + p {
    margin-bottom: 4pt;
}

h4 + p {
    margin-bottom: 6pt;
}

/* Achievement bullets */
ul li strong:first-child {
    color: #2c5aa0;
}

/* Education section */
body > h2:nth-last-of-type(4) ~ * {
    page-break-inside: avoid;
}

/* Prevent orphans and widows */
h2, h3, h4 {
    page-break-after: avoid;
}

li {
    page-break-inside: avoid;
}

/* Link styling */
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
    <title>Arthur Sherman - Resume</title>
</head>
<body>
    {html_content}
</body>
</html>
"""

# Configure fonts
font_config = FontConfiguration()

# Generate PDF
HTML(string=full_html).write_pdf(
    'Arthur_Sherman_Resume_QA_CSM.pdf',
    stylesheets=[CSS(string=css_content, font_config=font_config)],
    font_config=font_config
)

print("✓ PDF generated successfully: Arthur_Sherman_Resume_QA_CSM.pdf")
