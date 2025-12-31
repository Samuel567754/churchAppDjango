"""
Test Keep-Alive and Health Check Endpoints
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChurchApp.settings')
django.setup()

from django.test import RequestFactory
from settings.views import keep_alive, health_check

def test_keep_alive():
    """Test the keep-alive endpoint"""
    print("=" * 60)
    print("TESTING KEEP-ALIVE ENDPOINT")
    print("=" * 60)
    
    factory = RequestFactory()
    request = factory.get('/settings/keep-alive/')
    
    try:
        response = keep_alive(request)
        print(f"\n✅ Status Code: {response.status_code}")
        
        import json
        data = json.loads(response.content)
        print(f"✅ Response: {json.dumps(data, indent=2)}")
        
        if data.get('status') == 'alive':
            print("\n🎉 Keep-alive endpoint is working correctly!")
        else:
            print("\n⚠️ Keep-alive endpoint returned unexpected status")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "=" * 60)
    print("TESTING HEALTH CHECK ENDPOINT")
    print("=" * 60)
    
    factory = RequestFactory()
    request = factory.get('/settings/health/')
    
    try:
        response = health_check(request)
        print(f"\n✅ Status Code: {response.status_code}")
        
        import json
        data = json.loads(response.content)
        print(f"✅ Response: {json.dumps(data, indent=2)}")
        
        if data.get('status') == 'healthy':
            print("\n🎉 Health check endpoint is working correctly!")
        else:
            print("\n⚠️ Health check shows issues - review checks above")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🔍 KEEP-ALIVE ENDPOINT TEST SUITE")
    print("=" * 60)
    
    try:
        test_keep_alive()
        test_health_check()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
        print("\nNext Steps:")
        print("1. Deploy to Render: git push origin main")
        print("2. Test production endpoint:")
        print("   curl https://church-app-oukg.onrender.com/settings/keep-alive/")
        print("3. Set up UptimeRobot monitor (see KEEP_ALIVE_SETUP.md)")
        print("4. Monitor your app at https://uptimerobot.com/")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
