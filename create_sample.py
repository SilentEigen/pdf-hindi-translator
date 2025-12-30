from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_pdf(path):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "Understanding AI")
    
    # Subheading
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 700, "What is Machine Learning?")
    
    # Paragraph
    c.setFont("Helvetica", 12)
    text = """Machine Learning is a subset of artificial intelligence. 
It focuses on building systems that learn from data. 
For example, self-driving cars use computer vision to navigate."""
    
    y = 650
    for line in text.split('\n'):
        c.drawString(100, y, line)
        y -= 20
        
    c.showPage()
    
    # Page 2
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "Deep Learning")
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, "Deep learning uses neural networks with many layers.")
    
    c.save()

if __name__ == "__main__":
    create_sample_pdf("input/sample.pdf")
