from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime

app = Flask(__name__)

# Enhanced tasks with more fields
tasks = []
task_id_counter = 0


@app.route("/")
def index():
    # Sort tasks: incomplete first, then by priority
    sorted_tasks = sorted(tasks, key=lambda x: (x["completed"], -x["priority"]))
    return render_template("index.html", tasks=sorted_tasks)


@app.route("/add", methods=["POST"])
def add_task():
    global task_id_counter
    title = request.form.get("task")
    priority = int(request.form.get("priority", 2))
    category = request.form.get("category", "General")

    if title:
        task_id_counter += 1
        tasks.append({
            "id": task_id_counter,
            "title": title,
            "completed": False,
            "priority": priority,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    # Remove using list comprehension - no need for global
    tasks[:] = [t for t in tasks if t["id"] != task_id]
    return redirect("/")


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            break
    return redirect("/")


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    new_title = request.form.get("new_title")
    new_priority = int(request.form.get("new_priority", 2))
    new_category = request.form.get("new_category", "General")

    for task in tasks:
        if task["id"] == task_id:
            if new_title:
                task["title"] = new_title
            task["priority"] = new_priority
            task["category"] = new_category
            break
    return redirect("/")


@app.route("/clear_completed", methods=["POST"])
def clear_completed():
    # Remove completed tasks - no need for global
    tasks[:] = [t for t in tasks if not t["completed"]]
    return redirect("/")


@app.route("/stats")
def get_stats():
    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    pending = total - completed
    return jsonify({
        "total": total,
        "completed": completed,
        "pending": pending
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)