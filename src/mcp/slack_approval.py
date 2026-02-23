from typing import Optional
import os
from flask import Flask, request, render_template_string

HTML_RESPONSE = """
<html>
  <head><title>Task Approval</title></head>
  <body>
    <h2>Task {{ task_id }} - {{ status }}</h2>
    <p>{{ message }}</p>
    <p><a href="/">Back to pending tasks</a></p>
  </body>
</html>
"""


class SlackApprovalServer:
    """Lightweight approval HTTP server using Flask.

    Usage:
      server = SlackApprovalServer(host='0.0.0.0', port=5000)
      server.start(tool_registry)

    The server exposes:
      - GET /           : list pending tasks (awaiting_approval) and evidence review tasks (awaiting_evidence_approval)
      - GET /approve/<task_id>?token=... : approve task proposal, agent can begin execution
      - GET /reject/<task_id>?token=...  : reject task proposal
      - GET /approve_evidence/<task_id>?token=... : approve submitted evidence; agent receives proposed_cost
      - GET /reject_evidence/<task_id>?token=... : reject evidence; task returns to executing for retry
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.app: Optional[Flask] = None
        self.registry = None

    def start(self, registry, debug: bool = False):
        from flask import Flask

        self.registry = registry
        app = Flask(__name__)

        @app.route("/")
        def index():
            pending = registry.get_pending_real_world_tasks()
            awaiting_evidence = registry.get_awaiting_evidence_tasks()
            html = ["<h1>Real-World Task Management</h1>"]
            
            # Pending approval
            if pending:
                html.append("<h2>Pending Approval</h2><ul>")
                base = os.environ.get("APPROVAL_BASE_URL") or f"http://{self.host}:{self.port}"
                token = os.environ.get("APPROVAL_TOKEN")
                for t in pending:
                    approve = f"{base}/approve/{t['id']}"
                    reject = f"{base}/reject/{t['id']}"
                    if token:
                        approve += f"?token={token}"
                        reject += f"?token={token}"
                    proposed = t.get("proposed_cost", 0)
                    outcome = t.get("expected_outcome", "")
                    html.append(f"<li><strong>Task {t['id']}</strong> (Agent: {t['agent_id']}, Cost: {proposed})<br/>Expected: {outcome}<br/><a href=\"{approve}\">Approve</a> | <a href=\"{reject}\">Reject</a></li>")
                html.append("</ul>")
            else:
                html.append("<p><em>No pending approvals</em></p>")
            
            # Awaiting evidence review
            if awaiting_evidence:
                html.append("<h2>Awaiting Evidence Review</h2><ul>")
                base = os.environ.get("APPROVAL_BASE_URL") or f"http://{self.host}:{self.port}"
                token = os.environ.get("APPROVAL_TOKEN")
                for t in awaiting_evidence:
                    approve = f"{base}/approve_evidence/{t['id']}"
                    reject = f"{base}/reject_evidence/{t['id']}"
                    if token:
                        approve += f"?token={token}"
                        reject += f"?token={token}"
                    proposed = t.get("proposed_cost", 0)
                    html.append(f"<li><strong>Task {t['id']}</strong> (Agent: {t['agent_id']}, Reward: {proposed})<br/><a href=\"{approve}\">Approve Evidence</a> | <a href=\"{reject}\">Reject Evidence</a></li>")
                html.append("</ul>")
            else:
                html.append("<p><em>No pending evidence review</em></p>")
            
            return "".join(html)

        @app.route("/approve/<task_id>")
        def approve(task_id):
            token = request.args.get("token")
            expected = os.environ.get("APPROVAL_TOKEN")
            if expected and token != expected:
                return render_template_string(HTML_RESPONSE, task_id=task_id, status="error", message="Invalid token"), 403
            ok = registry.approve_real_world_task(task_id)
            if ok:
                return render_template_string(HTML_RESPONSE, task_id=task_id, status="approved", message="Task approved. Agent can now begin execution.")
            return render_template_string(HTML_RESPONSE, task_id=task_id, status="error", message="Task not found or already processed"), 404

        @app.route("/reject/<task_id>")
        def reject(task_id):
            token = request.args.get("token")
            expected = os.environ.get("APPROVAL_TOKEN")
            if expected and token != expected:
                return render_template_string(HTML_RESPONSE, task_id=task_id, status="error", message="Invalid token"), 403
            reason = request.args.get("reason", "No reason provided")
            ok = registry.reject_real_world_task(task_id, reason)
            if ok:
                return render_template_string(HTML_RESPONSE, task_id=task_id, status="rejected", message=f"Task rejected: {reason}")
            return render_template_string(HTML_RESPONSE, task_id=task_id, status="error", message="Task not found or already processed"), 404

        @app.route("/approve_evidence/<task_id>")
        def approve_evidence(task_id):
            token = request.args.get("token")
            expected = os.environ.get("APPROVAL_TOKEN")
            if expected and token != expected:
                return render_template_string(HTML_RESPONSE, task_id=task_id, status="error", message="Invalid token"), 403
            ok = registry.approve_task_evidence(task_id)
            if ok:
                return render_template_string(HTML_RESPONSE, task_id=task_id, status="evidence_approved", message="Evidence approved. Agent will receive the proposed cost on next turn.")
            return render_template_string(HTML_RESPONSE, task_id=task_id, status="error", message="Task not found or not awaiting evidence review"), 404

        @app.route("/reject_evidence/<task_id>")
        def reject_evidence(task_id):
            token = request.args.get("token")
            expected = os.environ.get("APPROVAL_TOKEN")
            if expected and token != expected:
                return render_template_string(HTML_RESPONSE, task_id=task_id, status="error", message="Invalid token"), 403
            reason = request.args.get("reason", "Evidence does not meet requirements")
            ok = registry.reject_task_evidence(task_id, reason)
            if ok:
                return render_template_string(HTML_RESPONSE, task_id=task_id, status="evidence_rejected", message=f"Evidence rejected: {reason}. Task returned to executing for retry.")
            return render_template_string(HTML_RESPONSE, task_id=task_id, status="error", message="Task not found or not awaiting evidence review"), 404

        self.app = app
        app.run(host=self.host, port=self.port, debug=debug)
