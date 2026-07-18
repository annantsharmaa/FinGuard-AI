"""
Design tokens and HTML render helpers for the Streamlit UI.

Palette
  ink-navy   #14213D  headers, sidebar, primary text on light
  paper      #F4F5F7  page background
  card       #FFFFFF  card surfaces
  line       #DDE1E8  hairline borders/dividers
  slate      #55607A  secondary/muted text
  stamp-red    #8C2F2F  high risk / rejected
  stamp-amber  #A6741A  pending review
  stamp-green  #2F6B4F  cleared / approved

Type
  Newsreader        display serif   — page title, section headers
  IBM Plex Sans     body text
  IBM Plex Mono     data — document IDs, scores, timestamps, filenames

Signature element: the "ledger stamp" — a dashed-border circular badge,
slightly rotated, used consistently everywhere a status or score is shown
(risk score, review decision, pending-queue badges). One device, reused,
rather than a different widget style per page.
"""

import html

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,500;0,600;1,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --ink: #14213D;
    --paper: #F4F5F7;
    --card: #FFFFFF;
    --line: #DDE1E8;
    --slate: #55607A;
    --red: #8C2F2F;
    --amber: #A6741A;
    --green: #2F6B4F;
}

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--ink); }

/* ---- App background ---- */
[data-testid="stAppViewContainer"] { background: var(--paper); }
[data-testid="stHeader"] { background: transparent; }

/* ---- Sidebar: the ledger spine ---- */
[data-testid="stSidebar"] {
    background: var(--ink);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] * { color: #E7E9F0 !important; }
[data-testid="stSidebar"] label { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; letter-spacing: 0.04em; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15); }

/* radio nav rows */
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 0.45rem 0.6rem;
    border-radius: 4px;
    margin-bottom: 2px;
    transition: background 0.15s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,0.08); }

/* ---- Headings ---- */
h1, h2, h3, .fg-display {
    font-family: 'Newsreader', serif;
    font-weight: 600;
    letter-spacing: -0.01em;
}
h1 { font-size: 2.1rem !important; }
h2 { font-size: 1.35rem !important; margin-top: 1.6rem !important; }
h3 { font-size: 1.05rem !important; }

/* ---- Eyebrow / wordmark header ---- */
.fg-header { margin-bottom: 0.4rem; }
.fg-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--slate);
    margin-bottom: 0.15rem;
}
.fg-rule { border: none; border-top: 1px solid var(--line); margin: 0.9rem 0 1.4rem 0; }

/* ---- Cards ---- */
.fg-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
}
.fg-card-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--slate);
    margin-bottom: 0.6rem;
}

/* ---- Finding rows ---- */
.fg-finding {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.92rem;
}
.fg-finding:last-child { border-bottom: none; }
.fg-finding-mark {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    width: 1.1rem;
    flex-shrink: 0;
}
.fg-finding-pass .fg-finding-mark { color: var(--green); }
.fg-finding-fail .fg-finding-mark { color: var(--red); }
.fg-finding-rule { font-weight: 600; margin-right: 0.35rem; }
.fg-finding-detail { color: var(--slate); }

/* ---- The ledger stamp (signature element) ---- */
.fg-stamp-wrap { display: flex; align-items: center; gap: 1.1rem; margin: 0.6rem 0 1.2rem 0; }
.fg-stamp {
    width: 92px; height: 92px;
    border-radius: 50%;
    border: 2.5px dashed var(--stamp-color, var(--slate));
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    transform: rotate(-7deg);
    flex-shrink: 0;
    color: var(--stamp-color, var(--slate));
}
.fg-stamp-score { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 1.5rem; line-height: 1; }
.fg-stamp-max { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; opacity: 0.8; }
.fg-stamp-status {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--stamp-color, var(--slate));
}
.fg-stamp-meta { font-size: 0.82rem; color: var(--slate); margin-top: 0.1rem; }

/* ---- Small status pill (used in tables / queue rows) ---- */
.fg-pill {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    border: 1px solid var(--pill-color, var(--slate));
    color: var(--pill-color, var(--slate));
}

/* ---- Custom table for All Documents ---- */
.fg-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.fg-table th {
    text-align: left;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--slate);
    border-bottom: 1px solid var(--line);
    padding: 0.5rem 0.6rem;
}
.fg-table td {
    padding: 0.55rem 0.6rem;
    border-bottom: 1px solid var(--line);
    vertical-align: middle;
}
.fg-table tr:last-child td { border-bottom: none; }
.fg-mono { font-family: 'IBM Plex Mono', monospace; }

/* ---- Agent log timeline ---- */
.fg-log-entry { border-left: 2px solid var(--line); padding: 0.15rem 0 0.9rem 1rem; margin-left: 0.3rem; position: relative; }
.fg-log-entry::before {
    content: ""; position: absolute; left: -5px; top: 0.35rem;
    width: 8px; height: 8px; border-radius: 50%; background: var(--ink);
}
.fg-log-agent { font-weight: 600; font-size: 0.9rem; }
.fg-log-time { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: var(--slate); }
.fg-log-io { font-size: 0.84rem; color: var(--slate); margin-top: 0.15rem; }

/* ---- Buttons ---- */
[data-testid="stButton"] button {
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.03em;
    border: 1px solid var(--ink);
}
[data-testid="baseButton-primary"] { background: var(--ink); }

/* ---- File uploader / inputs ---- */
[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed var(--line);
    background: var(--card);
    border-radius: 6px;
}

[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 6px; background: var(--card); }
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title, eyebrow):
    import streamlit as st
    st.markdown(
        f"""
        <div class="fg-header">
            <div class="fg-eyebrow">{html.escape(eyebrow)}</div>
            <h1 class="fg-display">{html.escape(title)}</h1>
        </div>
        <hr class="fg-rule"/>
        """,
        unsafe_allow_html=True,
    )


def _status_color(status):
    return {
        "auto_cleared": "var(--green)",
        "approved": "var(--green)",
        "pending_review": "var(--amber)",
        "rejected": "var(--red)",
    }.get(status, "var(--slate)")


def stamp(score, status, caption=None):
    """The signature 'ledger stamp' badge — used for risk score + decisions."""
    import streamlit as st
    color = _status_color(status)
    label = status.replace("_", " ")
    caption_html = f'<div class="fg-stamp-meta">{html.escape(caption)}</div>' if caption else ""
    st.markdown(
        f"""
        <div class="fg-stamp-wrap">
            <div class="fg-stamp" style="--stamp-color:{color};">
                <div class="fg-stamp-score">{score}</div>
                <div class="fg-stamp-max">/ 100</div>
            </div>
            <div>
                <div class="fg-stamp-status" style="color:{color};">{html.escape(label)}</div>
                {caption_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(status):
    color = _status_color(status)
    return f'<span class="fg-pill" style="--pill-color:{color};">{html.escape(status.replace("_", " "))}</span>'


def card_start(title=None):
    import streamlit as st
    title_html = f'<div class="fg-card-title">{html.escape(title)}</div>' if title else ""
    st.markdown(f'<div class="fg-card">{title_html}', unsafe_allow_html=True)


def card_end():
    import streamlit as st
    st.markdown("</div>", unsafe_allow_html=True)


def render_findings(findings):
    """Render a list of finding dicts as styled pass/fail rows."""
    import streamlit as st
    rows = []
    for f in findings:
        cls = "fg-finding-pass" if f["passed"] else "fg-finding-fail"
        mark = "✓" if f["passed"] else "✕"
        rule = f["rule_name"].replace("_", " ").title()
        rows.append(
            f'<div class="fg-finding {cls}">'
            f'<div class="fg-finding-mark">{mark}</div>'
            f'<div><span class="fg-finding-rule">{html.escape(rule)}</span>'
            f'<span class="fg-finding-detail">{html.escape(f["detail"])}</span></div>'
            f'</div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def render_agent_log(entries):
    import streamlit as st
    if not entries:
        st.caption("No log entries.")
        return
    rows = []
    for e in entries:
        rows.append(
            f'<div class="fg-log-entry">'
            f'<span class="fg-log-agent">{html.escape(e["agent_name"])}</span> '
            f'<span class="fg-log-time">{html.escape(str(e["timestamp"]))}</span>'
            f'<div class="fg-log-io"><b>in:</b> {html.escape(str(e["input_summary"]))}</div>'
            f'<div class="fg-log-io"><b>out:</b> {html.escape(str(e["output_summary"]))}</div>'
            f'</div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def render_documents_table(docs):
    import streamlit as st
    if not docs:
        st.caption("No documents processed yet.")
        return
    rows = []
    for d in docs:
        status = d.get("status") or "—"
        pill_html = pill(status) if d.get("status") else "—"
        score = d.get("score")
        score_str = f'{score}' if score is not None else "—"
        rows.append(
            f"<tr>"
            f'<td class="fg-mono">{d["id"]}</td>'
            f'<td>{html.escape(d["filename"])}</td>'
            f'<td>{html.escape(d.get("doc_type") or "—")}</td>'
            f'<td class="fg-mono">{score_str}</td>'
            f'<td>{pill_html}</td>'
            f'<td class="fg-mono">{html.escape(str(d.get("uploaded_at") or ""))}</td>'
            f"</tr>"
        )
    st.markdown(
        f"""
        <table class="fg-table">
            <thead><tr><th>ID</th><th>Filename</th><th>Type</th><th>Score</th><th>Status</th><th>Uploaded</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
