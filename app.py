from flask import Flask, request, redirect, render_template_string
import requests, json, os
from datetime import datetime
from supabase import create_client

app = Flask(__name__)

DISCORD_CLIENT_ID = os.getenv("CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
DISCORD_REDIRECT_URI = "https://your-render-app.onrender.com/callback"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

auth_page = """
<html>
<head>
<title>認証中...</title>
<style>
body {
  background-color: #0d0d0d;
  color: white;
  font-family: 'Poppins', sans-serif;
  text-align: center;
  padding-top: 15%;
}
.button {
  background: #5865F2;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 18px;
  color: white;
  text-decoration: none;
}
</style>
</head>
<body>
  <h1>Discord 認証</h1>
  <a class="button" href="https://discord.com/api/oauth2/authorize?client_id={{cid}}&redirect_uri={{redirect}}&response_type=code&scope=identify%20email">認証を開始する</a>
</body>
</html>
"""

success_page = """
<html><head><title>認証成功</title></head>
<body style="background:#0d0d0d;color:white;text-align:center;padding-top:15%;">
<h1>✅ 認証が完了しました</h1>
<p>このウィンドウを閉じてDiscordに戻ってください。</p>
</body></html>
"""

@app.route("/auth")
def auth():
    return render_template_string(auth_page, cid=DISCORD_CLIENT_ID, redirect=DISCORD_REDIRECT_URI)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    r.raise_for_status()
    tokens = r.json()
    access_token = tokens["access_token"]

    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    existing = supabase.table("verify_users").select("*").eq("id", user["id"]).execute()
    if existing.data:
        return "このユーザーはすでに認証済みです。"

    supabase.table("verify_users").insert({
        "id": user["id"],
        "username": f"{user['username']}#{user['discriminator']}",
        "email": user.get("email", "None"),
        "ip": ip,
        "time": datetime.now().isoformat()
    }).execute()

    requests.post(WEBHOOK_URL, json={
        "embeds": [{
            "title": "🆕 新しい認証",
            "fields": [
                {"name": "ユーザー", "value": f"{user['username']}#{user['discriminator']}"},
                {"name": "ID", "value": user["id"]},
                {"name": "Email", "value": user.get("email", 'N/A')},
                {"name": "IP", "value": ip}
            ],
            "color": 5763719
        }]
    })

    return success_page

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
