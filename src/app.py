"""
Analytics Copilot - Streamlit Chat Application

This is the main Streamlit application that integrates all three agents
(Schema Linker, SQL Generator, Validator) into an interactive chat interface.

The application provides:
- Natural language to SQL conversion
- Automatic schema linking using RAG
- SQL validation with self-correction
- Interactive result visualization
- Chat-based interface for the Olist Brazilian E-Commerce dataset

Usage:
    streamlit run src/app.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from typing import Any

from src.utils.snowflake_conn import get_session
from src.utils.config import get_config
from src.agents.schema_linker import link_schema
from src.agents.sql_generator import generate_sql
from src.agents.validator import validate_and_execute
from src.utils.viz import auto_chart


# Page configuration
st.set_page_config(
    page_title="Analytics Copilot",
    page_icon="🤖",
    layout="wide"
)


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    # Initialize message history
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Initialize Snowflake session
    if 'snowflake_session' not in st.session_state:
        try:
            st.session_state.snowflake_session = get_session()
            st.session_state.connection_status = "Connected"
        except Exception as e:
            st.session_state.snowflake_session = None
            st.session_state.connection_status = f"Connection failed: {str(e)}"


def render_sidebar():
    """Render the sidebar with title, connection status, dataset selector, and instructions."""
    with st.sidebar:
        st.title("🤖 Analytics Copilot")

        # Connection status indicator
        st.subheader("Connection Status")
        if st.session_state.connection_status == "Connected":
            st.success("✓ Connected to Snowflake")
        else:
            st.error(f"✗ {st.session_state.connection_status}")

        st.divider()

        # Dataset info
        st.subheader("Dataset")
        st.info("📊 Olist Brazilian E-Commerce")

        st.divider()

        # Instructions
        st.subheader("How to Use")
        st.markdown("""
        **Ask questions about your data in natural language!**

        **Examples:**
        - "What are the top 5 product categories by revenue?"
        - "Show me monthly order trends over time"
        - "Which customers have the highest average review score?"
        - "What's the average delivery time by customer state?"
        - "Which customers have placed the most orders?"

        **Features:**
        - 🔍 Automatic schema detection
        - 🤖 AI-powered SQL generation
        - ✅ Query validation & auto-correction
        - 📊 Smart visualizations
        - 💬 Chat-based interface

        **Tips:**
        - Be specific with your questions
        - Ask about trends, aggregations, or comparisons
        - Review the generated SQL in the expander
        """)

        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def display_chat_history():
    """Display all messages in the chat history (text only — no expanders or charts to avoid re-render ghosts)."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])



def process_user_question(question: str):
    """
    Process user question through the complete agent pipeline.

    Pipeline:
    1. Schema Linker: Find relevant tables
    2. SQL Generator: Generate SQL query
    3. Validator: Validate and execute with auto-correction
    4. Visualization: Auto-generate chart

    Args:
        question: User's natural language question
    """
    session = st.session_state.snowflake_session

    if session is None:
        st.error("❌ No active Snowflake connection. Please check your credentials.")
        return

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(question)

    # Create assistant message placeholder
    with st.chat_message("assistant"):
        # Create placeholder for status updates
        status_placeholder = st.empty()
        response_placeholder = st.empty()

        try:
            # Step 1: Schema Linking
            status_placeholder.info("🔍 Finding relevant tables...")
            cfg = get_config()
            schema_context = link_schema(session, question)

            if not schema_context:
                error_msg = "❌ Could not find relevant tables for your question. Please try rephrasing or check if the data exists."
                response_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                return

            # Step 2: SQL Generation
            status_placeholder.info("🤖 Generating SQL query...")
            sql_query = generate_sql(session, question, schema_context)

            if not sql_query or not sql_query.strip():
                error_msg = "❌ Could not generate SQL query. The LLM may be unavailable or the question is unclear."
                response_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                return

            # Step 3: Validation and Execution
            status_placeholder.info("✅ Validating and executing query...")
            max_retries = cfg.get("sql_generator", {}).get("max_retries", 3)
            final_sql, result = validate_and_execute(
                session, sql_query, question, schema_context, max_retries=max_retries
            )

            # Clear status
            status_placeholder.empty()

            # Check if result is an error (string) or success (DataFrame)
            if isinstance(result, str):
                # Execution failed after all retries
                error_msg = f"❌ Query execution failed after multiple attempts:\n\n{result}"
                response_placeholder.error(error_msg)

                # Still show the SQL and tables for debugging
                with st.expander("📋 Relevant Tables Found", expanded=False):
                    for table in schema_context:
                        st.markdown(f"**{table['table_name']}** (Relevance: {table['relevance_score']:.2f})")
                        for col in table["columns"]:
                            st.text(f"  - {col['column_name']} ({col['data_type']}): {col['description']}")

                with st.expander("💻 Failed SQL Query", expanded=True):
                    st.code(final_sql, language="sql")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "metadata": {
                        "tables": schema_context,
                        "sql": final_sql
                    }
                })
                return

            # Success! Convert Snowpark DataFrame to Pandas
            result_df = result.to_pandas()

            # Check if result is empty
            if result_df.empty:
                response_placeholder.warning("⚠️ Query executed successfully but returned no results.")
                success_msg = "✅ Query executed successfully, but no data matched your criteria."
            else:
                success_msg = f"✅ Found {len(result_df)} result(s)!"

            response_placeholder.success(success_msg)

            # Show relevant tables in expander
            with st.expander("📋 Relevant Tables Found", expanded=False):
                for table in schema_context:
                    st.markdown(f"**{table['table_name']}** (Relevance: {table['relevance_score']:.2f})")
                    for col in table["columns"]:
                        st.text(f"  - {col['column_name']} ({col['data_type']}): {col['description']}")

            # Show SQL in expander
            with st.expander("💻 Show SQL", expanded=False):
                st.code(final_sql, language="sql")

            # Show results dataframe (cap display at 1000 rows to prevent browser lag)
            if not result_df.empty:
                st.subheader("📊 Results")
                display_df = result_df.head(1000)
                if len(result_df) > 1000:
                    st.caption(f"Showing first 1,000 of {len(result_df):,} rows. Refine your query with a LIMIT for fewer results.")
                st.dataframe(display_df, use_container_width=True)

                # Generate and show chart
                chart = auto_chart(result_df)
                if chart is not None:
                    st.subheader("📈 Visualization")
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("💡 No automatic visualization available for this data structure.")

            # Add assistant response to message history (no chart/df — avoids re-render ghosts)
            st.session_state.messages.append({
                "role": "assistant",
                "content": success_msg,
                "metadata": {
                    "tables": schema_context,
                    "sql": final_sql,
                }
            })

        except Exception as e:
            # Catch-all error handler
            error_msg = f"❌ An unexpected error occurred: {str(e)}"
            status_placeholder.empty()
            response_placeholder.error(error_msg)

            st.error("**Error Details:**")
            st.exception(e)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main area - Header
    st.title("💬 Analytics Copilot Chat")
    st.markdown("Ask questions about your data in natural language, and I'll generate SQL queries and visualizations for you!")

    # Display chat history
    display_chat_history()

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Process the user's question
        process_user_question(prompt)


if __name__ == "__main__":
    main()
