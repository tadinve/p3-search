#!/usr/bin/env python3
"""
Script to create a test PDF with tables for testing the table-aware document processing
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

def create_test_pdf():
    """Create a PDF with tables and regular text for testing"""
    filename = "test_document_with_tables.pdf"
    
    # Check if file already exists
    if os.path.exists(filename):
        print(f"Test PDF already exists: {filename}")
        return filename
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    # Get sample style sheet
    styles = getSampleStyleSheet()
    
    # Content to add to the PDF
    content = []
    
    # Add title
    title = Paragraph("Test Document with Tables", styles['Title'])
    content.append(title)
    content.append(Spacer(1, 12))
    
    # Add introductory text
    intro_text = Paragraph(
        "This document contains both regular text and tables to test the table-aware document processing functionality.",
        styles['Normal']
    )
    content.append(intro_text)
    content.append(Spacer(1, 12))
    
    # Create first table - Employee Information
    table1_data = [
        ['Employee ID', 'Name', 'Department', 'Salary', 'Start Date'],
        ['EMP001', 'John Smith', 'Engineering', '$85,000', '2022-01-15'],
        ['EMP002', 'Sarah Johnson', 'Marketing', '$70,000', '2021-06-20'],
        ['EMP003', 'Mike Chen', 'Engineering', '$90,000', '2020-03-10'],
        ['EMP004', 'Lisa Davis', 'HR', '$65,000', '2023-02-01'],
        ['EMP005', 'Tom Wilson', 'Sales', '$75,000', '2022-09-05']
    ]
    
    table1 = Table(table1_data)
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(Paragraph("Employee Information Table", styles['Heading2']))
    content.append(Spacer(1, 12))
    content.append(table1)
    content.append(Spacer(1, 12))
    
    # Add some regular text between tables
    middle_text = Paragraph(
        "The above table shows employee information including salaries and start dates. "
        "Below is another table with different information about products.",
        styles['Normal']
    )
    content.append(middle_text)
    content.append(Spacer(1, 12))
    
    # Create second table - Product Information
    table2_data = [
        ['Product Code', 'Product Name', 'Category', 'Price', 'Stock'],
        ['PROD001', 'Wireless Headphones', 'Electronics', '$129.99', '45'],
        ['PROD002', 'Coffee Mug', 'Kitchen', '$19.99', '120'],
        ['PROD003', 'Office Chair', 'Furniture', '$299.99', '15'],
        ['PROD004', 'Notebook Set', 'Stationery', '$24.99', '80'],
        ['PROD005', 'USB Cable', 'Electronics', '$12.99', '200']
    ]
    
    table2 = Table(table2_data)
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(Paragraph("Product Inventory Table", styles['Heading2']))
    content.append(Spacer(1, 12))
    content.append(table2)
    content.append(Spacer(1, 12))
    
    # Add concluding text
    conclusion_text = Paragraph(
        "This document demonstrates how tables should be processed as complete rows rather than individual cells. "
        "When searching for 'John Smith', the entire employee record should be returned as a single unit. "
        "Similarly, searching for 'Wireless Headphones' should return the complete product information.",
        styles['Normal']
    )
    content.append(conclusion_text)
    
    # Build the PDF
    doc.build(content)
    print(f"Test PDF created: {filename}")
    return filename

if __name__ == "__main__":
    try:
        create_test_pdf()
    except ImportError:
        print("reportlab library is required to create the test PDF.")
        print("Install it with: pip install reportlab")
        print("Alternatively, you can create your own PDF with tables for testing.")