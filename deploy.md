Render is an excellent choice for deploying Streamlit apps, as it natively supports Python web services with automatic scaling and free tiers. [peerdh](https://peerdh.com/blogs/programming-insights/deploying-your-streamlit-app-on-render)

## Prerequisites
- A GitHub repository containing your Streamlit app (e.g., `research-team/dashboards` with `app.py` and `requirements.txt`).
- A free Render account at [render.com](https://render.com).
- Ensure `requirements.txt` lists all dependencies, including `streamlit` (generate via `pip freeze > requirements.txt` locally if needed). [pythonandvba](https://pythonandvba.com/blog/deploy-your-streamlit-app-to-render-free-heroku-alternative/)

## Step 1: Prepare Your Repository
Push your code to GitHub if not already done.

```bash
cd research-team/dashboards
git init  # If new repo
git add .
git commit -m "Initial Streamlit app for Render"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

Verify `app.py` runs locally: `streamlit run app.py`. [youtube](https://www.youtube.com/watch?v=bXRVgg2iWyc)

## Step 2: Create Render Service
1. Log in to [render.com](https://render.com) and click **New > Web Service**.
2. Select your GitHub repository (authorise if prompted).
3. Configure as follows:
   | Setting          | Value                                      |
   |------------------|--------------------------------------------|
   | Name             | e.g., `research-dashboards`                |
   | Environment      | `Python 3`                                 |
   | Region           | Closest to Johannesburg (e.g., Oregon)     |
   | Branch           | `main`                                     |
   | Root Directory   | `.` (or `research-team/dashboards` if nested) |
   | Build Command    | `pip install -r requirements.txt`          |
   | Start Command    | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` |

4. Select **Free** instance type and click **Create Web Service**. [youtube](https://www.youtube.com/watch?v=4SO3CUWPYf0)

## Step 3: Monitor Deployment
- Watch the **Logs** tab for build progress (installs pip packages, then starts Streamlit).
- Deployment takes 2–5 minutes; your live URL (e.g., `https://research-dashboards.onrender.com`) appears once ready.
- Free tier spins down after 15 minutes of inactivity (cold start ~30s). [pythonandvba](https://pythonandvba.com/blog/deploy-your-streamlit-app-to-render-free-heroku-alternative/)

## Step 4: Environment Variables (If Needed)
Add secrets (e.g., API keys) via **Environment** tab:
- Key: e.g., `STREAMLIT_SERVER_PORT`, Value: `$PORT`
- Key: e.g., `API_KEY`, Value: `your-secret` [community.render](https://community.render.com/t/streamlit-python-project-error/7532)

## Auto-Deploy Updates
Edit code locally, commit, and push to `main`:
```bash
git add .
git commit -m "Update dashboard"
git push
```
Render auto-detects and redeploys in ~1–2 minutes. [youtube](https://www.youtube.com/watch?v=bXRVgg2iWyc)

## Troubleshooting
- **Build fails**: Check `requirements.txt` for compatible versions; pin Python packages if needed (e.g., `streamlit==1.38.0`).
- **Port error**: Always use `$PORT` and `0.0.0.0` in start command.
- **Cold starts**: Upgrade to paid tier ($7/mo) for always-on. View logs for details. [4geeks](https://4geeks.com/lesson/deploy-model-using-streamlit-and-render)