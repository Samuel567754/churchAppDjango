# Keep-Alive Setup Guide for Render & Supabase Free Tiers

## Problem
Both Render and Supabase free tier services go to sleep after periods of inactivity:
- **Render Free Tier**: Spins down after 15 minutes of inactivity
- **Supabase Free Tier**: Pauses database after 7 days of inactivity

## Solution
Use **UptimeRobot** (free service) to ping your application every 5 minutes, keeping both services active.

---

## Step 1: Keep-Alive Endpoints Created ✅

Two endpoints have been added to your application:

### 1. **Keep-Alive Endpoint** (Lightweight)
```
URL: https://your-app.onrender.com/settings/keep-alive/
```
- Performs minimal database query
- Returns JSON response
- Specifically designed for UptimeRobot pinging

### 2. **Health Check Endpoint** (Detailed)
```
URL: https://your-app.onrender.com/settings/health/
```
- Provides detailed health status
- Checks database and model access
- Useful for monitoring

---

## Step 2: Set Up UptimeRobot (Free)

### A. Create UptimeRobot Account

1. Go to **https://uptimerobot.com/**
2. Click **"Sign Up for Free"**
3. Create your free account (50 monitors included)
4. Verify your email address

### B. Create a Monitor for Your App

1. **Log in to UptimeRobot Dashboard**
2. Click **"+ Add New Monitor"**

3. **Configure Monitor:**
   ```
   Monitor Type: HTTP(s)
   Friendly Name: Church App Keep-Alive
   URL: https://church-app-oukg.onrender.com/settings/keep-alive/
   Monitoring Interval: 5 minutes
   Monitor Timeout: 30 seconds
   ```

4. **Advanced Settings (Optional):**
   - Alert Contacts: Add your email to receive alerts if the site goes down
   - HTTP Method: GET
   - Expected Status Code: 200

5. Click **"Create Monitor"**

### C. Monitor Response

UptimeRobot will now:
- Ping your app every 5 minutes
- Keep Render from spinning down
- Keep Supabase database active
- Alert you if the site goes down

---

## Step 3: Verify Setup

### Test Locally (Development)
```bash
# Start your development server
python manage.py runserver

# In another terminal or browser, test the endpoint
curl http://127.0.0.1:8000/settings/keep-alive/
```

**Expected Response:**
```json
{
  "status": "alive",
  "message": "Server is active",
  "timestamp": "2025-12-31T18:59:48.123456",
  "database": "connected",
  "purpose": "Prevent Render and Supabase from sleeping"
}
```

### Test Health Check
```bash
curl http://127.0.0.1:8000/settings/health/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-31T18:59:48.123456",
  "checks": {
    "database": "connected",
    "models": "accessible (5 users)"
  }
}
```

### Test Production (After Deployment)
```bash
curl https://church-app-oukg.onrender.com/settings/keep-alive/
curl https://church-app-oukg.onrender.com/settings/health/
```

---

## Step 4: Deploy to Render

### Update Your Render App

1. **Commit and Push Changes:**
   ```bash
   git add .
   git commit -m "Add keep-alive endpoints for UptimeRobot"
   git push origin main
   ```

2. **Render will auto-deploy** (if auto-deploy is enabled)

3. **Manual Deploy** (if needed):
   - Go to Render Dashboard
   - Select your service
   - Click "Manual Deploy" → "Deploy latest commit"

### Verify Deployment

Once deployed, test the endpoint:
```bash
curl https://your-app.onrender.com/settings/keep-alive/
```

---

## Step 5: Optional - GitHub Actions Backup

As an additional backup, you can use GitHub Actions to ping your site:

### Create `.github/workflows/keep-alive.yml`

```yaml
name: Keep Alive - Prevent Sleep

on:
  schedule:
    # Runs every 5 minutes
    - cron: '*/5 * * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  keep-alive:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Keep-Alive Endpoint
        run: |
          echo "Pinging keep-alive endpoint..."
          response=$(curl -s -w "\n%{http_code}" https://church-app-oukg.onrender.com/settings/keep-alive/)
          http_code=$(echo "$response" | tail -n1)
          body=$(echo "$response" | sed \$d)
          
          echo "Response: $body"
          echo "HTTP Code: $http_code"
          
          if [ "$http_code" -eq 200 ]; then
            echo "✅ Server is alive!"
          else
            echo "❌ Server returned unexpected status: $http_code"
            exit 1
          fi
```

**Note:** GitHub Actions is a backup solution. UptimeRobot is the primary method.

---

## Understanding the Free Tier Limits

### Render Free Tier
- ✅ **750 hours/month** of runtime (enough for 24/7 operation)
- ⚠️ Spins down after **15 minutes** of inactivity
- ⚠️ Cold start time: **30-60 seconds**
- ✅ **Solution:** Ping every 5 minutes

### Supabase Free Tier
- ✅ **500 MB database**
- ✅ **Unlimited API requests**
- ⚠️ Pauses after **7 days** of inactivity
- ⚠️ Limited to **2 active projects**
- ✅ **Solution:** Database queries from keep-alive endpoint

### UptimeRobot Free Tier
- ✅ **50 monitors**
- ✅ **5-minute monitoring interval**
- ✅ **2-month log retention**
- ✅ **Unlimited alerts**

---

## Monitoring Dashboard

### Access Your Monitors

1. Go to **https://uptimerobot.com/dashboard**
2. View your monitors:
   - **Uptime percentage**
   - **Response times**
   - **Recent events**
   - **Downtime alerts**

### Set Up Alerts

1. Click on **"My Settings"**
2. Add **Alert Contacts:**
   - Email
   - SMS (limited on free tier)
   - Webhook
   - Slack integration

3. Configure when to receive alerts:
   - On every down
   - On every up
   - Never

---

## Troubleshooting

### Issue: Endpoint Returns 404

**Solution:**
```bash
# Verify URL is correct
https://your-app.onrender.com/settings/keep-alive/  # ✅ Correct
https://your-app.onrender.com/keep-alive/           # ❌ Missing /settings/

# Check if app is deployed
# Check Render logs
```

### Issue: Endpoint Returns 500

**Solution:**
1. Check Render logs for errors
2. Verify database connection in Render environment variables
3. Test health endpoint: `/settings/health/`

### Issue: UptimeRobot Shows Down

**Possible Causes:**
- Render is deploying (temporary)
- Database connection issue
- Cold start taking too long (increase timeout to 60s)

**Solution:**
- Wait for deployment to complete
- Check Render and Supabase status pages
- Increase monitor timeout in UptimeRobot

### Issue: Still Sleeping After Setup

**Check:**
1. UptimeRobot monitor is active (not paused)
2. Monitoring interval is 5 minutes
3. Endpoint URL is correct
4. Render environment variables are set correctly

---

## Best Practices

### 1. **Monitor Multiple Endpoints**
Create separate monitors for:
- Main site: `https://your-app.onrender.com/`
- Keep-alive: `https://your-app.onrender.com/settings/keep-alive/`
- Health check: `https://your-app.onrender.com/settings/health/`

### 2. **Set Up Proper Alerts**
- Add email notifications
- Use Slack/Discord webhooks for team alerts
- Don't over-alert (use reasonable thresholds)

### 3. **Monitor Response Times**
- Review UptimeRobot graphs weekly
- Identify slow performance patterns
- Optimize if response times consistently > 2 seconds

### 4. **Regular Maintenance**
- Check UptimeRobot dashboard weekly
- Review Render logs for errors
- Monitor Supabase usage

### 5. **Database Connection Pooling**
Already configured in your settings.py:
```python
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,  # Connection pooling
        ssl_require=True
    )
}
```

---

## Cost Considerations

### Current Setup (100% Free)
- ✅ Render Free Tier: $0/month
- ✅ Supabase Free Tier: $0/month
- ✅ UptimeRobot Free: $0/month
- **Total: $0/month** 🎉

### When to Upgrade

**Render Paid Plan ($7/month):**
- No cold starts
- Always-on instances
- More memory/CPU

**Supabase Pro ($25/month):**
- Never pauses
- More storage
- Better performance
- Point-in-time recovery

**UptimeRobot Pro ($7/month):**
- 1-minute monitoring interval
- SMS alerts
- More monitors

---

## Alternative Solutions

### 1. **Cron-Job.org** (Free Alternative)
- Similar to UptimeRobot
- Website: https://cron-job.org/
- Set up to ping your endpoint every 5 minutes

### 2. **Freshping** (Free Alternative)
- 50 checks, 1-minute interval
- Website: https://www.freshworks.com/website-monitoring/

### 3. **Pingdom** (Paid)
- More advanced monitoring
- Better analytics
- Starts at $10/month

---

## Monitoring Checklist

- [ ] Keep-alive endpoint is accessible
- [ ] Health check endpoint is accessible
- [ ] UptimeRobot account created
- [ ] Monitor added and active in UptimeRobot
- [ ] Monitoring interval set to 5 minutes
- [ ] Alert contacts configured
- [ ] Tested endpoint locally
- [ ] Tested endpoint in production
- [ ] Verified Render doesn't sleep for 24 hours
- [ ] Verified database stays active

---

## Support & Resources

### Documentation
- Render: https://render.com/docs
- Supabase: https://supabase.com/docs
- UptimeRobot: https://uptimerobot.com/kb/

### Status Pages
- Render: https://status.render.com/
- Supabase: https://status.supabase.com/
- GitHub: https://www.githubstatus.com/

### Community
- Render Community: https://community.render.com/
- Supabase Discord: https://discord.supabase.com/

---

## Summary

Your church app now has:
1. ✅ Lightweight keep-alive endpoint (`/settings/keep-alive/`)
2. ✅ Detailed health check endpoint (`/settings/health/`)
3. ✅ Ready for UptimeRobot monitoring
4. ✅ Prevents Render from sleeping
5. ✅ Keeps Supabase database active
6. ✅ 100% free solution

**Next Step:** Set up your UptimeRobot monitor and enjoy uninterrupted service! 🚀
