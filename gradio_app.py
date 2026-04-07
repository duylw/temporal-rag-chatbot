import logging
import gradio as gr
import httpx

logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"


async def get_response(query: str) -> str:
    """Fetch response from the Agentic RAG API"""
    if not query.strip():
        return "Please enter a question."

    try:
        url = f"{API_BASE_URL}/agentic_ask/"
        params = {"question": query}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, params=params)
            
            if response.status_code != 200:
                return f"**Error: API returned status {response.status_code}**\n\nDetails: {response.text}"

            data = response.json()
            
            answer = data.get("answer", "No answer found.")
            rewritten_query = data.get("rewritten_query", "")
            sources = data.get("sources", [])
            n_iterations = data.get("n_iterations", 0)
            execution_time = data.get("execution_time", 0.0)
            guardrail = data.get("guardrail_result")

            # Build the answer UI (Clean, text-based layout)
            formatted_response = answer
            
            # --- Metadata ---
            formatted_response += "\n\n<br>\n\n### Execution Details\n"
            if rewritten_query and rewritten_query != query:
                formatted_response += f"- **Rewritten Query:** {rewritten_query}\n"
            formatted_response += f"- **Agent Iterations:** {n_iterations}\n"
            formatted_response += f"- **Execution Time:** {execution_time:.2f}s\n"
            
            if guardrail:
                formatted_response += f"- **Guardrails:** {guardrail}\n"

            # --- Sources ---
            if sources:
                formatted_response += "\n### Sources Used\n"
                for i, doc in enumerate(sources, 1):
                    metadata = doc.get("metadata", {})
                    source_name = metadata.get("source", metadata.get("video_name", f"Document {i}"))
                    timestamp = metadata.get("timestamp")
                    timestamp_str = f" (Timestamp: {timestamp})" if timestamp else ""
                    
                    formatted_response += f"{i}. **{source_name}**{timestamp_str}\n"

            return formatted_response

    except httpx.RequestError as e:
        return f"Connection error: {str(e)}\n\nMake sure the API server is running at {API_BASE_URL}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def create_gradio_interface():
    """Create and configure the Gradio interface"""

    # Using a modern, typography-focused theme
    theme = gr.themes.Default(
        primary_hue="zinc",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"]
    )

    with gr.Blocks(title="Agentic RAG Assistant", theme=theme) as interface:
        gr.Markdown(
            """
            # Agentic RAG Assistant
            
            Ask complex questions about your indexed documents. The agent will iteratively search, rewrite queries, and evaluate its answers.
            """
        )

        with gr.Row():
            with gr.Column(scale=4):
                query_input = gr.Textbox(
                    show_label=False,
                    placeholder="Ask a question about your documents...", 
                    lines=1, 
                    max_lines=5,
                    container=False
                )

            with gr.Column(scale=1):
                submit_btn = gr.Button("Search", variant="primary")

        response_output = gr.Markdown(
            value="_Awaiting your question..._", 
            elem_classes=["response-markdown"]
        )

        gr.Examples(
            examples=[
                ["What is the main topic of the documents?"],
                ["Can you summarize the key findings?"],
            ],
            inputs=[query_input],
            label="Example queries"
        )

        # Handle submission
        submit_btn.click(
            fn=get_response,
            inputs=[query_input],
            outputs=[response_output],
        )

        # Handle Enter key
        query_input.submit(
            fn=get_response,
            inputs=[query_input],
            outputs=[response_output],
        )

    return interface


demo = create_gradio_interface()

def main():
    """Main entry point for the Gradio app"""
    print("Starting Agentic RAG Gradio Interface...")
    print(f"API Base URL: {API_BASE_URL}")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()