import streamlit as st
import requests
import pandas as pd
import time
import json
from typing import List, Dict, Any

# Configuration
API_BASE_URL = "http://api-backend:8000"  # Docker internal URL
# For local development, use: "http://localhost:8000"

def get_api_url():
    """Get the appropriate API URL based on environment"""
    import os
    # Check for environment variable first, then fallback to local detection
    api_url = os.getenv("API_BASE_URL")
    if api_url:
        return api_url
    
    # For local development detection
    if os.getenv("ENVIRONMENT") == "local":
        return "http://localhost:8000"
    return API_BASE_URL

# Page configuration
st.set_page_config(
    page_title="PDF Document Search",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        color: #1f77b4;
    }
    .search-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .result-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .danger-zone {
        background-color: #fff5f5;
        border: 2px solid #fed7d7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def upload_pdf():
    """Function to upload PDF documents"""
    st.markdown('<div class="main-header"><h2>📄 Upload PDF Documents</h2></div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose PDF files to upload",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files to add to the search database"
    )
    
    if uploaded_files:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Upload Documents", type="primary", use_container_width=True):
                upload_progress = st.progress(0)
                upload_status = st.empty()
                results = []
                
                for i, uploaded_file in enumerate(uploaded_files):
                    upload_status.info(f"Uploading {uploaded_file.name}...")
                    
                    try:
                        # Prepare file for upload
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        
                        # Upload to API
                        response = requests.post(
                            f"{get_api_url()}/upload-pdf",
                            files=files,
                            timeout=300
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            results.append({
                                "filename": uploaded_file.name,
                                "status": "✅ Success",
                                "document_id": result["document_id"],
                                "lines_processed": result["lines_processed"]
                            })
                            upload_status.success(f"✅ {uploaded_file.name} uploaded successfully!")
                        else:
                            results.append({
                                "filename": uploaded_file.name,
                                "status": "❌ Failed",
                                "error": response.text[:100]
                            })
                            upload_status.error(f"❌ Failed to upload {uploaded_file.name}")
                    
                    except Exception as e:
                        results.append({
                            "filename": uploaded_file.name,
                            "status": "❌ Error",
                            "error": str(e)[:100]
                        })
                        upload_status.error(f"❌ Error uploading {uploaded_file.name}: {str(e)}")
                    
                    # Update progress
                    upload_progress.progress((i + 1) / len(uploaded_files))
                
                # Display results
                st.markdown("### Upload Results")
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)
                
                # Success summary
                successful_uploads = len([r for r in results if "Success" in r["status"]])
                if successful_uploads > 0:
                    st.success(f"🎉 Successfully uploaded {successful_uploads} out of {len(uploaded_files)} documents!")

def list_documents():
    """Function to list all loaded documents"""
    st.markdown('<div class="main-header"><h2>📚 Document Library</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh Document List", type="secondary", use_container_width=True):
            st.rerun()
    
    try:
        # Get document list from API
        response = requests.get(f"{get_api_url()}/documents", timeout=10)
        
        if response.status_code == 200:
            documents = response.json()
            
            if documents:
                st.markdown("### 📋 Loaded Documents")
                
                # Create a DataFrame for better display
                df_data = []
                for doc in documents:
                    # Format upload date
                    upload_date = pd.to_datetime(doc['upload_date']).strftime('%Y-%m-%d %H:%M:%S')
                    
                    df_data.append({
                        "📄 Filename": doc['filename'],
                        "🆔 Document ID": doc['document_id'][:8] + "...",  # Shortened for display
                        "📅 Upload Date": upload_date,
                        "📊 Lines": doc['lines_count'],
                        "📖 Pages": f"{doc['first_page']}-{doc['last_page']}" if doc['first_page'] != doc['last_page'] else str(doc['first_page'])
                    })
                
                df = pd.DataFrame(df_data)
                
                # Display as a nice table
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Summary statistics
                st.markdown("### 📈 Library Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                total_docs = len(documents)
                total_lines = sum(doc['lines_count'] for doc in documents)
                total_pages = sum(doc['last_page'] - doc['first_page'] + 1 for doc in documents)
                avg_lines = total_lines / total_docs if total_docs > 0 else 0
                
                with col1:
                    st.metric("📚 Total Documents", total_docs)
                
                with col2:
                    st.metric("📝 Total Lines", f"{total_lines:,}")
                
                with col3:
                    st.metric("📖 Total Pages", total_pages)
                
                with col4:
                    st.metric("📊 Avg Lines/Doc", f"{avg_lines:.0f}")
                
                # Export option
                if st.button("📥 Export Document List as CSV"):
                    # Include full document IDs in export
                    export_data = []
                    for doc in documents:
                        upload_date = pd.to_datetime(doc['upload_date']).strftime('%Y-%m-%d %H:%M:%S')
                        export_data.append({
                            "filename": doc['filename'],
                            "document_id": doc['document_id'],
                            "upload_date": upload_date,
                            "lines_count": doc['lines_count'],
                            "first_page": doc['first_page'],
                            "last_page": doc['last_page']
                        })
                    
                    export_df = pd.DataFrame(export_data)
                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name="document_library.csv",
                        mime="text/csv"
                    )
                
                # Individual document actions
                st.markdown("### 🔍 Document Actions")
                selected_doc = st.selectbox(
                    "Select a document to view details:",
                    options=[f"{doc['filename']} ({doc['document_id'][:8]}...)" for doc in documents],
                    help="Choose a document to view its details or perform actions"
                )
                
                if selected_doc:
                    # Find the selected document
                    doc_index = [f"{doc['filename']} ({doc['document_id'][:8]}...)" for doc in documents].index(selected_doc)
                    selected_document = documents[doc_index]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📄 View Document Contents", use_container_width=True):
                            st.info(f"Document ID: {selected_document['document_id']}")
                            st.info(f"To view full contents, use the API endpoint: GET /documents/{selected_document['document_id']}")
                    
                    with col2:
                        if st.button("🔍 Search in This Document", use_container_width=True):
                            st.info("Use the Search Documents tab and filter results by document ID to search within this specific document.")
                    
                    with col3:
                        if st.button("🗑️ Delete Document", use_container_width=True, type="secondary"):
                            # Use session state to manage confirmation
                            if 'confirm_delete' not in st.session_state:
                                st.session_state.confirm_delete = False
                            
                            if not st.session_state.confirm_delete:
                                st.session_state.confirm_delete = True
                                st.rerun()
                    
                    # Show confirmation dialog if delete was clicked
                    if st.session_state.get('confirm_delete', False):
                        st.warning(f"⚠️ Are you sure you want to delete '{selected_document['filename']}'?")
                        col_confirm1, col_confirm2 = st.columns(2)
                        
                        with col_confirm1:
                            if st.button("✅ Yes, Delete", key="confirm_delete_btn", type="primary"):
                                try:
                                    delete_response = requests.delete(
                                        f"{get_api_url()}/documents/{selected_document['document_id']}",
                                        timeout=30
                                    )
                                    
                                    if delete_response.status_code == 200:
                                        result = delete_response.json()
                                        st.success(f"✅ Document '{result['filename']}' deleted successfully!")
                                        st.info(f"Deleted {result['deleted_lines']} lines")
                                        st.session_state.confirm_delete = False
                                        time.sleep(2)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed to delete document: {delete_response.text}")
                                        st.session_state.confirm_delete = False
                                
                                except Exception as e:
                                    st.error(f"❌ Error deleting document: {str(e)}")
                                    st.session_state.confirm_delete = False
                        
                        with col_confirm2:
                            if st.button("❌ Cancel", key="cancel_delete_btn"):
                                st.session_state.confirm_delete = False
                                st.rerun()
                
                # Bulk actions section
                st.markdown("### 🔧 Bulk Actions")
                st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
                st.error("⚠️ **Danger Zone** - These actions cannot be undone!")
                
                if st.button("🗑️ Delete All Documents", type="secondary", use_container_width=True):
                    # Use session state for bulk delete confirmation
                    if 'confirm_delete_all' not in st.session_state:
                        st.session_state.confirm_delete_all = False
                    
                    if not st.session_state.confirm_delete_all:
                        st.session_state.confirm_delete_all = True
                        st.rerun()
                
                # Show bulk delete confirmation
                if st.session_state.get('confirm_delete_all', False):
                    st.error("⚠️ **DANGER**: This will permanently delete ALL documents!")
                    st.write("Type 'DELETE ALL' to confirm:")
                    
                    confirmation_text = st.text_input("Confirmation:", key="delete_all_confirm")
                    
                    col_confirm1, col_confirm2 = st.columns(2)
                    with col_confirm1:
                        if st.button("💀 Confirm Deletion", key="confirm_delete_all_btn", type="primary", disabled=(confirmation_text != "DELETE ALL")):
                            try:
                                delete_response = requests.delete(
                                    f"{get_api_url()}/documents",
                                    timeout=30
                                )
                                
                                if delete_response.status_code == 200:
                                    result = delete_response.json()
                                    st.success(f"✅ {result['message']}")
                                    st.info(f"Deleted {result.get('deleted_documents', 0)} documents and {result.get('deleted_lines', 0)} lines")
                                    st.session_state.confirm_delete_all = False
                                    time.sleep(3)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to delete documents: {delete_response.text}")
                                    st.session_state.confirm_delete_all = False
                            
                            except Exception as e:
                                st.error(f"❌ Error deleting all documents: {str(e)}")
                                st.session_state.confirm_delete_all = False
                    
                    with col_confirm2:
                        if st.button("❌ Cancel All", key="cancel_delete_all_btn"):
                            st.session_state.confirm_delete_all = False
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.info("📭 No documents found in the library.")
                st.markdown("""
                ### 💡 Getting Started
                1. Go to the **Upload PDFs** tab
                2. Select one or more PDF files
                3. Click **Upload Documents**
                4. Return here to see your document library
                """)
        
        else:
            st.error(f"❌ Failed to fetch documents: {response.text}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {str(e)}")
        st.info("💡 Make sure the API backend service is running on the correct port.")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    # API Health status (always show)
    st.markdown("---")
    st.markdown("### 🏥 System Health")
    try:
        health_response = requests.get(f"{get_api_url()}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h4>🔗 API Backend</h4>
                    <p style="color: green; font-weight: bold;">✅ Healthy</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                vector_status = "✅ Connected" if health_data.get("vector_store_connected", False) else "❌ Disconnected"
                color = "green" if health_data.get("vector_store_connected", False) else "red"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🗄️ Vector Store</h4>
                    <p style="color: {color}; font-weight: bold;">{vector_status}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h4>⚡ Status</h4>
                    <p style="color: blue; font-weight: bold;">🟢 Ready</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("🔴 API Backend Offline")
    except:
        st.error("🔴 Cannot reach API Backend")

def search_documents():
    """Function to search documents"""
    st.markdown('<div class="main-header"><h2>🔍 Search Documents</h2></div>', unsafe_allow_html=True)
    
    # Search interface
    with st.container():
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Enter your search query:",
                placeholder="e.g., earthwork activities, ponding water, project management...",
                help="Search for keywords or phrases in your uploaded documents"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        
        # Advanced options
        with st.expander("⚙️ Advanced Search Options"):
            col1, col2 = st.columns(2)
            with col1:
                limit = st.slider("Maximum results", min_value=1, max_value=20, value=10)
            with col2:
                min_similarity = st.slider("Minimum similarity", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Perform search
    if search_button and search_query.strip():
        with st.spinner("🔍 Searching documents..."):
            try:
                # Prepare search request
                search_data = {
                    "query": search_query.strip(),
                    "limit": limit,
                    "min_similarity": min_similarity
                }
                
                # Send search request
                start_time = time.time()
                response = requests.post(
                    f"{get_api_url()}/search-doc",
                    json=search_data,
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    search_results = response.json()
                    
                    # Display search metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Results Found", search_results["number_of_results"])
                    
                    with col2:
                        st.metric("⏱️ Response Time", f"{search_results['response_time_ms']:.1f} ms")
                    
                    with col3:
                        st.metric("🎯 Min Similarity", f"{min_similarity:.2f}")
                    
                    with col4:
                        st.metric("🔢 Max Results", limit)
                    
                    # Display results
                    if search_results["results"]:
                        st.markdown("### 📋 Search Results")
                        
                        # Create DataFrame for table display
                        table_data = []
                        for i, result in enumerate(search_results["results"], 1):
                            table_data.append({
                                "📄 Document ID": result['document_id'][:12] + "...",  # Shortened for display
                                "📁 Name": result['filename'],
                                "📖 Page #": result['page_number'],
                                "📝 Line #": result['line_number'],
                                "🎯 Score": f"{result['similarity_score']:.2f}",
                                "📄 Text": result['text_fragment'][:100] + "..." if len(result['text_fragment']) > 100 else result['text_fragment']
                            })
                        
                        # Display the table
                        results_df = pd.DataFrame(table_data)
                        
                        # Configure column widths and display
                        st.dataframe(
                            results_df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "📄 Document ID": st.column_config.TextColumn(
                                    "Document ID",
                                    width="small",
                                    help="Unique identifier for the document"
                                ),
                                "📁 Name": st.column_config.TextColumn(
                                    "Filename",
                                    width="medium",
                                    help="Name of the PDF document"
                                ),
                                "📖 Page #": st.column_config.NumberColumn(
                                    "Page",
                                    width="small",
                                    help="Page number in the document"
                                ),
                                "📝 Line #": st.column_config.NumberColumn(
                                    "Line",
                                    width="small", 
                                    help="Line number in the document"
                                ),
                                "🎯 Score": st.column_config.TextColumn(
                                    "Similarity",
                                    width="small",
                                    help="Similarity score (0.00-1.00)"
                                ),
                                "📄 Text": st.column_config.TextColumn(
                                    "Text Fragment",
                                    width="large",
                                    help="Matching text content"
                                )
                            }
                        )
                        
                        # Show expandable full text for detailed view
                        with st.expander("� View Full Text Details"):
                            selected_result = st.selectbox(
                                "Select a result to view full text:",
                                options=[f"Result #{i+1} - {result['filename']} (Page {result['page_number']}, Line {result['line_number']})" 
                                        for i, result in enumerate(search_results["results"])],
                                help="Choose a result to see the complete text fragment"
                            )
                            
                            if selected_result:
                                # Find the selected result
                                result_index = int(selected_result.split("#")[1].split(" ")[0]) - 1
                                selected_result_data = search_results["results"][result_index]
                                
                                # Display full details
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    st.markdown("**� Document Details:**")
                                    st.write(f"**Document ID:** {selected_result_data['document_id']}")
                                    st.write(f"**Filename:** {selected_result_data['filename']}")
                                    st.write(f"**Page:** {selected_result_data['page_number']}")
                                    st.write(f"**Line:** {selected_result_data['line_number']}")
                                    st.write(f"**Similarity Score:** {selected_result_data['similarity_score']:.4f}")
                                
                                with col2:
                                    st.markdown("**📝 Full Text:**")
                                    st.markdown(f"""
                                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">
                                        {selected_result_data['text_fragment']}
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Export options
                        if st.button("📥 Export Results as CSV"):
                            # Create export DataFrame with full data
                            export_data = []
                            for result in search_results["results"]:
                                export_data.append({
                                    "document_id": result['document_id'],
                                    "filename": result['filename'],
                                    "page_number": result['page_number'],
                                    "line_number": result['line_number'],
                                    "similarity_score": f"{result['similarity_score']:.4f}",
                                    "text_fragment": result['text_fragment']
                                })
                            
                            export_df = pd.DataFrame(export_data)
                            csv = export_df.to_csv(index=False)
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=csv,
                                file_name=f"search_results_{search_query.replace(' ', '_')}.csv",
                                mime="text/csv"
                            )
                    else:
                        st.warning(f"🔍 No results found for '{search_query}' with similarity ≥ {min_similarity:.2f}")
                        st.info("💡 Try:\n- Different keywords\n- Lower similarity threshold\n- More general search terms")
                
                else:
                    st.error(f"❌ Search failed: {response.text}")
            
            except Exception as e:
                st.error(f"❌ Error during search: {str(e)}")
    
    elif search_button and not search_query.strip():
        st.warning("⚠️ Please enter a search query")

def main():
    """Main application"""
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=PDF+Search", use_column_width=True)
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "📍 Navigate to:",
            ["🔍 Search Documents", "📄 Upload PDFs", "📚 Document Library"],
            index=0
        )
        
        st.markdown("---")
        
        # System info
        st.markdown("### ℹ️ System Info")
        try:
            health_response = requests.get(f"{get_api_url()}/health", timeout=5)
            if health_response.status_code == 200:
                st.success("🟢 API Online")
            else:
                st.error("🔴 API Offline")
        except:
            st.error("🔴 API Unreachable")
        
        st.markdown("---")
        st.markdown("""
        ### 📖 How to Use
        1. **Upload PDFs** - Add documents to search
        2. **Search** - Find relevant content
        3. **Manage** - View and delete documents
        4. **Export** - Download results and data
        """)
    
    # Main content based on selected page
    if page == "🔍 Search Documents":
        search_documents()
    elif page == "📄 Upload PDFs":
        upload_pdf()
    elif page == "📚 Document Library":
        list_documents()

if __name__ == "__main__":
    main()