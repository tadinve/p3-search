#!/usr/bin/env python3
"""
Test script to verify improved similarity scoring
"""
import requests
import json

def test_similarity_scoring():
    """Test the improved similarity scoring with exact matches"""
    
    # First, upload a document containing "ponding water"
    test_content = """
    This document discusses various water management issues.
    The main concern is ponding water in low-lying areas.
    Ponding water can cause significant drainage problems.
    Water ponding is a common issue in urban planning.
    """
    
    # Create a test PDF-like document
    upload_url = "http://localhost:8001/upload-text"
    
    upload_data = {
        "filename": "test_ponding_water.txt",
        "content": test_content
    }
    
    print("🔍 Testing Improved Similarity Scoring")
    print("=" * 50)
    
    try:
        # Upload test document
        print("📤 Uploading test document...")
        upload_response = requests.post(upload_url, json=upload_data)
        if upload_response.status_code == 200:
            print("✅ Document uploaded successfully")
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            return
        
        # Test search with exact phrase
        search_url = "http://localhost:8001/search"
        
        test_queries = [
            "ponding water",
            "water ponding", 
            "drainage problems",
            "urban planning",
            "completely unrelated term"
        ]
        
        for query in test_queries:
            print(f"\n🔎 Searching for: '{query}'")
            
            search_data = {
                "query": query,
                "limit": 5,
                "min_similarity": 0.0  # Get all results to see scores
            }
            
            search_response = requests.post(search_url, json=search_data)
            if search_response.status_code == 200:
                results = search_response.json()
                
                if results:
                    for i, result in enumerate(results[:3], 1):
                        score = result.get('similarity_score', 0)
                        content = result.get('content', '')[:60] + "..."
                        print(f"  {i}. Score: {score:.4f} | {content}")
                else:
                    print("  No results found")
            else:
                print(f"  ❌ Search failed: {search_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_similarity_scoring()