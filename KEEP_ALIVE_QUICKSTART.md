# Quick Start: Keep Render & Supabase Alive with UptimeRobot

## TL;DR - What Was Done

✅ **Created 2 Endpoints:**
1. `/settings/keep-alive/` - Lightweight ping endpoint
2. `/settings/health/` - Detailed health check

✅ **Purpose:**
- Prevent Render from sleeping (spins down after 15 min)
- Keep Supabase database active (pauses after 7 days)

✅ **How It Works:**
- UptimeRobot pings `/settings/keep-alive/` every 5 minutes
- Endpoint performs minimal database query
- Keeps both services active 24/7

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Deploy Your Code
```bash
git add .
git commit -m "Add keep-alive endpoints"
git push origin main
```

### Step 2: Test Endpoint (after deployment)
```bash
curl https://church-app-oukg.onrender.com/settings/keep-alive/
```

**Expected Response:**
```json
{
  "status": "alive",
  "message": "Server is active",
  "timestamp": "2025-12-31T19:00:00",
  "database": "connected"
}
```

### Step 3: Set Up UptimeRobot

1. Go to **https://uptimerobot.com/signup**
2. Create free account
3. Click **"+ Add New Monitor"**
4. Configure:
   ```
   Type: HTTP(s)
   Name: Church App Keep-Alive
   URL: https://church-app-oukg.onrender.com/settings/keep-alive/
   Interval: 5 minutes
   ```
5. Click **"Create Monitor"**

### Step 4: Done! ✅

Your app will now stay active 24/7 for free.

---

## 📊 Monitor Your App

**UptimeRobot Dashboard:** https://uptimerobot.com/dashboard

You'll see:
- ✅ Uptime percentage
- ✅ Response times
- ✅ Recent pings
- ✅ Downtime alerts

---

## 🔍 Verify Everything Works

### Test Locally (Before Deploying)
```bash
# Run test script
python test_keep_alive.py

# Or start server and test manually
python manage.py runserver
# Visit: http://127.0.0.1:8000/settings/keep-alive/
```

### Test in Production (After Deploying)
```bash
# Quick test
curl https://church-app-oukg.onrender.com/settings/keep-alive/

# Detailed health check
curl https://church-app-oukg.onrender.com/settings/health/
```

---

## 📁 Files Created

1. **`settings/views.py`** - Added keep_alive() and health_check() functions
2. **`settings/urls.py`** - Added URL routes
3. **`KEEP_ALIVE_SETUP.md`** - Full detailed guide
4. **`test_keep_alive.py`** - Test script
5. **`KEEP_ALIVE_QUICKSTART.md`** - This file

---

## ⚡ Endpoints Reference

### Keep-Alive Endpoint (Use This for UptimeRobot)
```
URL: /settings/keep-alive/
Method: GET
Auth: Not required
Response: JSON
Purpose: Lightweight ping to keep services alive
```

### Health Check Endpoint
```
URL: /settings/health/
Method: GET
Auth: Not required
Response: JSON with detailed status
Purpose: Detailed health monitoring
```

---

## 🎯 Why This Works

**Render Free Tier:**
- Sleeps after 15 minutes of no activity
- Ping every 5 minutes keeps it awake
- 750 hours/month free (enough for 24/7)

**Supabase Free Tier:**
- Pauses after 7 days of no database activity
- Keep-alive does a database query each ping
- Keeps database active indefinitely

**UptimeRobot Free Tier:**
- 50 monitors free
- 5-minute interval free
- Unlimited pings

**Total Cost: $0/month** 🎉

---

## 🐛 Troubleshooting

### Problem: 404 Error
**Fix:** Make sure URL is exactly:
```
https://church-app-oukg.onrender.com/settings/keep-alive/
```
(Note the `/settings/` prefix)

### Problem: 500 Error
**Fix:** Check Render logs for errors
```bash
# In Render dashboard:
Logs → View logs
```

### Problem: UptimeRobot Shows "Down"
**Fix:**
1. Wait 60 seconds (could be cold start)
2. Increase monitor timeout to 60 seconds
3. Check Render deployment status

---

## 📚 More Information

For detailed instructions, see:
- **`KEEP_ALIVE_SETUP.md`** - Complete setup guide
- **UptimeRobot Docs:** https://uptimerobot.com/kb/
- **Render Docs:** https://render.com/docs

---

## ✅ Success Checklist

- [ ] Code deployed to Render
- [ ] `/settings/keep-alive/` returns 200 OK
- [ ] UptimeRobot account created
- [ ] Monitor configured and active
- [ ] App hasn't slept for 24+ hours
- [ ] Email alerts configured in UptimeRobot

---

## 🎯 That's It!

Your church app will now stay active 24/7 without sleeping.

**Questions?** Check `KEEP_ALIVE_SETUP.md` for detailed information.

**Still having issues?** Review Render logs and UptimeRobot dashboard.
