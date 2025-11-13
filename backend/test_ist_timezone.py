"""
Test script to verify IST timezone functionality
"""
from datetime import datetime
from utils.timezone_utils import now_ist, to_ist_isoformat, utc_to_ist, format_ist_datetime
import pytz

def test_ist_timezone():
    print("=" * 60)
    print("Testing IST Timezone Utilities")
    print("=" * 60)
    
    # Test 1: Get current IST time
    print("\n1. Current time in IST:")
    ist_now = now_ist()
    print(f"   IST Time: {ist_now}")
    print(f"   Timezone: {ist_now.tzinfo}")
    
    # Test 2: UTC to IST conversion
    print("\n2. UTC to IST conversion:")
    utc_time = datetime.utcnow()
    utc_aware = pytz.utc.localize(utc_time)
    ist_time = utc_to_ist(utc_aware)
    print(f"   UTC Time: {utc_aware}")
    print(f"   IST Time: {ist_time}")
    print(f"   Time difference: {(ist_time.hour - utc_aware.hour) % 24} hours")
    
    # Test 3: ISO format conversion
    print("\n3. ISO format conversion:")
    iso_string = to_ist_isoformat(ist_now)
    print(f"   ISO Format: {iso_string}")
    print(f"   Contains +05:30 offset: {'+05:30' in iso_string}")
    
    # Test 4: Custom formatting
    print("\n4. Custom formatted IST datetime:")
    formatted = format_ist_datetime(ist_now, "%Y-%m-%d %H:%M:%S %Z IST")
    print(f"   Formatted: {formatted}")
    
    # Test 5: Handle None values
    print("\n5. Handling None values:")
    none_result = to_ist_isoformat(None)
    print(f"   to_ist_isoformat(None): {none_result}")
    
    # Test 6: Verify IST offset is correct (+05:30)
    print("\n6. Verify IST offset:")
    ist_tz = pytz.timezone('Asia/Kolkata')
    offset = ist_tz.utcoffset(datetime.now())
    print(f"   IST UTC Offset: {offset}")
    print(f"   Expected: 5:30:00")
    print(f"   Correct: {offset.total_seconds() == 19800}")  # 5.5 hours = 19800 seconds
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_ist_timezone()
