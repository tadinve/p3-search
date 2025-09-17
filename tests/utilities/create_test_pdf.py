#!/usr/bin/env python3
"""
Create Test PDF with Table Content
"""

try:
    import os
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    
    def create_table_test_pdf():
        # Save in tests directory
        tests_dir = os.path.dirname(os.path.dirname(__file__))
        filename = os.path.join(tests_dir, "table_test_document.pdf")
        
        # Check if file already exists
        if os.path.exists(filename):
            print(f"Table test PDF already exists: {filename}")
            return filename
            
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, "Test Document with Table Data")
        
        # Employee Table
        y_position = height - 120
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y_position, "Employee Information:")
        
        y_position -= 30
        c.setFont("Helvetica", 10)
        
        # Table headers
        headers = ["Employee ID", "Name", "Department", "Salary"]
        x_positions = [72, 172, 272, 372]
        
        for i, header in enumerate(headers):
            c.drawString(x_positions[i], y_position, header)
        
        # Table data - each row should be treated as one unit
        employees = [
            ["EMP001", "John Smith", "Engineering", "$85,000"],
            ["EMP002", "Jane Doe", "Marketing", "$75,000"],
            ["EMP003", "Bob Johnson", "Sales", "$70,000"]
        ]
        
        y_position -= 20
        for emp in employees:
            for i, data in enumerate(emp):
                c.drawString(x_positions[i], y_position, data)
            y_position -= 20
        
        # Product Table
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y_position, "Product Catalog:")
        
        y_position -= 30
        c.setFont("Helvetica", 10)
        
        # Product headers
        headers = ["Product Code", "Name", "Category", "Price"]
        for i, header in enumerate(headers):
            c.drawString(x_positions[i], y_position, header)
        
        # Product data
        products = [
            ["PROD001", "Wireless Headphones", "Electronics", "$129.99"],
            ["PROD002", "Coffee Mug", "Kitchen", "$19.99"],
            ["PROD003", "Office Chair", "Furniture", "$299.99"]
        ]
        
        y_position -= 20
        for prod in products:
            for i, data in enumerate(prod):
                c.drawString(x_positions[i], y_position, data)
            y_position -= 20
        
        c.save()
        print(f"✅ Created test PDF: {filename}")
        return filename
    
    if __name__ == "__main__":
        create_table_test_pdf()

except ImportError:
    import os
    print("⚠️  reportlab not available, creating simple text version...")
    
    # Fallback to simple text file approach
    content = """Table Processing Test Document

Employee Information Table:
Employee ID | Name | Department | Salary
EMP001 | John Smith | Engineering | $85,000
EMP002 | Jane Doe | Marketing | $75,000
EMP003 | Bob Johnson | Sales | $70,000

Product Catalog Table:
Product Code | Name | Category | Price  
PROD001 | Wireless Headphones | Electronics | $129.99
PROD002 | Coffee Mug | Kitchen | $19.99
PROD003 | Office Chair | Furniture | $299.99

This document contains structured data in table format.
Each row should be treated as a single unit for search purposes.
When searching for "John Smith", the entire employee record should be findable.
When searching for "Wireless Headphones", the complete product information should be available.
"""
    
    # Save in tests directory
    tests_dir = os.path.dirname(os.path.dirname(__file__))
    txt_file = os.path.join(tests_dir, "table_test_document.txt")
    with open(txt_file, "w") as f:
        f.write(content)
    
    print(f"✅ Created test text file: {txt_file}")
    print("💡 Note: For proper PDF testing, install reportlab: pip install reportlab")