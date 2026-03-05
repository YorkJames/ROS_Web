from flask import Flask, render_template, request, redirect, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = "change_this_secret"

WEB_USER = "admin"
WEB_PASS = "admin"

ROS_Active_URL = "http://10.10.13.251/rest/ppp/active"
ROS_Secret_URL = "http://10.10.13.251/rest/ppp/secret"
ROS_EXECUTE_URL = "http://10.10.13.251/rest/execute"
ROS_AUTH = ("root", "toor")


PPP_SECRET_CACHE = []
PPP_SECRET_LOADED = False

def load_ppp_secret():
    global PPP_SECRET_CACHE, PPP_SECRET_LOADED

    if PPP_SECRET_LOADED:
        return

    r = requests.get(
        ROS_Secret_URL,
        auth=ROS_AUTH,
        verify=False,
        timeout=5
    )
    r.raise_for_status()

    PPP_SECRET_CACHE = r.json()
    PPP_SECRET_LOADED = True

@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("login"):
        return render_template("index.html", logged_in=True)

    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        if user == WEB_USER and pwd == WEB_PASS:
            session["login"] = True
            return redirect("/")
        else:
            return render_template(
                "index.html",
                logged_in=False,
                error="Incorrect account or password"
            )

    return render_template("index.html", logged_in=False)

@app.route("/api/ppp/status")
def ppp_status():
    if not session.get("login"):
        return jsonify({"error": "unauthorized"}), 401

    try:
        load_ppp_secret()

        r_active = requests.get(
            ROS_Active_URL,
            auth=ROS_AUTH,
            verify=False,
            timeout=5
        )
        r_active.raise_for_status()
        actives = r_active.json()

        active_map = {
            a.get("name"): a
            for a in actives
            if a.get("name")
        }

        result = []
        for s in PPP_SECRET_CACHE:
            name = s.get("name")
            active = active_map.get(name)

            result.append({
                "name": name,
                "online": True if active else False,
                "caller_id": active.get("caller-id") if active else "",
                "uptime": active.get("uptime") if active else ""
            })

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reboot", methods=["POST"])
def reboot():
    if not session.get("login"):
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "missing ppp name"}), 400

    name = data["name"]

    if not name.startswith("ppp") or not name[3:].isdigit() or int(name[3:]) > 10:
        return jsonify({"error": "invalid ppp name"}), 400

    script_cmd = (
        f"/ppp/secret/disable {name}; "
        f"/interface/l2tp-server/remove <l2tp-{name}>; "
        f":delay 10s; "
        f"/ppp/secret/enable {name}"
    )

    try:
        r = requests.post(
            ROS_EXECUTE_URL,
            auth=ROS_AUTH,
            json={"script": script_cmd},
            verify=False,
            timeout=15
        )
        r.raise_for_status()

        return jsonify({
            "status": "ok",
            "name": name,
            "message": f"{name} reboot command executed"
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=80, debug=False)