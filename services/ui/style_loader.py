import os
import streamlit as st
import base64


def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def inject_local_font(font_path, font_name):
    if not os.path.exists(font_path):
        return
    
    with open(font_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    ext = os.path.splitext(font_path)[1].lstrip(".")
    fmt = {"otf": "opentype"}.get(ext, ext)
    mime = {"otf": "font/otf"}.get(ext, f"font/{ext}")

    st.markdown(f"""
        <style>
        @font-face {{
            font-family: '{font_name}';
            src: url('data:{mime};base64,{encoded}') format('{fmt}');
            font-weight: 100 900;
            font-style: normal;
        }}
        </style>
    """, unsafe_allow_html=True)

import streamlit.components.v1 as components


def suppress_injected_script_text():
    """Injects JS DOM MutationObserver into parent document to catch and hide any third-party injected script text."""
    components.html(
        """
        <script>
        (function() {
            try {
                const targetDoc = window.parent ? window.parent.document : document;
                
                if (window.parent) {
                    if (typeof window.parent.findAndPatch === 'undefined') {
                        window.parent.findAndPatch = function() {};
                    }
                    if (typeof window.parent.injectIntoIframe === 'undefined') {
                        window.parent.injectIntoIframe = function() {};
                    }
                }

                function purgeScriptText() {
                    try {
                        const walker = targetDoc.createTreeWalker(
                            targetDoc.body || targetDoc.documentElement,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );
                        let node;
                        while (node = walker.nextNode()) {
                            if (node.nodeValue && (node.nodeValue.includes('findAndPatch') || node.nodeValue.includes('injectIntoIframe'))) {
                                node.nodeValue = '';
                                if (node.parentElement && node.parentElement.tagName !== 'BODY' && node.parentElement.tagName !== 'HTML') {
                                    node.parentElement.style.display = 'none';
                                }
                            }
                        }
                    } catch (e) {}
                }

                purgeScriptText();
                const observer = new MutationObserver(purgeScriptText);
                observer.observe(targetDoc.documentElement || targetDoc.body, {
                    childList: true,
                    subtree: true,
                    characterData: true
                });
            } catch(err) {}
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def inject_webrtc_styles():
    suppress_injected_script_text()
    font_path = os.path.join(os.getcwd(), "static", "AdobeClean.otf")
    
    if not os.path.exists(font_path):
        return

    with open(font_path, "rb") as font_file:
        encoded_font = base64.b64encode(font_file.read()).decode()

    st.markdown(f"""
        <style>
        @font-face {{
            font-family: 'AdobeClean';
            src: url('data:font/otf;base64,{encoded_font}') format('opentype');
            font-weight: 100 900;
            font-style: normal;
        }}
        .MuiButtonBase-root,
        .MuiButton-root,
        .MuiButton-contained,
        .MuiButton-text {{
            border-radius: 4px !important;
            font-family: 'AdobeClean', sans-serif !important;
            letter-spacing: 0.05em !important;
        }}
        </style>
    """, unsafe_allow_html=True)