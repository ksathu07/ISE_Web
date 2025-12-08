from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess
import json
import os

app = Flask(__name__)
app.secret_key = "secret"  # Required for flash messages

OUTPUT_FOLDER = "build/reports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def run_ise_text(text):
    """
    Save the pasted text to a temporary file, run ISE.exe, and remove the temp file.
    """
    temp_input = "temp_input.txt"
    with open(temp_input, "w", encoding="utf-8") as f:
        f.write(text)
    
    # Run ISE.exe on the temporary file
    result = subprocess.run(
        ["ISE.exe", "-i", temp_input, "-o", OUTPUT_FOLDER],
        capture_output=True,
        text=True
    )
    os.remove(temp_input)
    return result.stdout, result.stderr

@app.route("/", methods=["GET", "POST"])
def index():
    report = None
    if request.method == "POST":
        text = request.form.get("text_input", "").strip()
        if not text:
            flash("Please paste some text to analyze.")
            return redirect(url_for("index"))

        # Run ISE on the pasted text
        stdout, stderr = run_ise_text(text)

        # Get the latest JSON report generated
        json_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]
        if not json_files:
            flash("ISE did not produce a report.")
            return redirect(url_for("index"))

        latest_report = max(
            [os.path.join(OUTPUT_FOLDER, f) for f in json_files],
            key=os.path.getctime
        )

        with open(latest_report, "r", encoding="utf-8") as f:
            report = json.load(f)

    return render_template("index.html", report=report)

if __name__ == "__main__":
   import os
   port = int(os.environ.get("PORT", 5000))
   app.run(host="0.0.0.0", port=port)