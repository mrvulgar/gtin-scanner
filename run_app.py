from gtin_scanner_live import app as gr_app


if __name__ == "__main__":
    # Run Gradio directly and disable API schema rendering on the UI
    gr_app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        inbrowser=False,
        share=False,
    )


