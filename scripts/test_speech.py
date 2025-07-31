#!/usr/bin/env python3
"""
Test Azure Speech Services Connection

Simple script to test the connection to Azure Speech Services
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_speech_services():
    """Test Azure Speech Services connection"""
    
    # Check required environment variables
    speech_key = os.getenv('AZURE_SPEECH_KEY')
    speech_region = os.getenv('AZURE_SPEECH_REGION')
    
    if not speech_key:
        print("❌ Error: AZURE_SPEECH_KEY not found in environment variables")
        return False
    
    if not speech_region:
        print("❌ Error: AZURE_SPEECH_REGION not found in environment variables")
        return False
    
    print(f"✅ Found Azure Speech Key: {speech_key[:8]}...")
    print(f"✅ Found Azure Speech Region: {speech_region}")
    
    try:
        # Import Azure Speech SDK
        import azure.cognitiveservices.speech as speechsdk
        print("✅ Azure Speech SDK imported successfully")
        
        # Create speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )
        
        # Test with a simple synthesis
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        print("🧪 Testing speech synthesis...")
        result = synthesizer.speak_text_async("Hello, this is a test.").get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("✅ Speech synthesis test successful!")
            return True
        else:
            print(f"❌ Speech synthesis failed: {result.reason}")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                print(f"❌ Cancellation reason: {cancellation.reason}")
                if cancellation.error_details:
                    print(f"❌ Error details: {cancellation.error_details}")
            return False
            
    except ImportError as e:
        print(f"❌ Error importing Azure Speech SDK: {e}")
        print("💡 Try installing with: pip install azure-cognitiveservices-speech")
        return False
    except Exception as e:
        print(f"❌ Error testing speech services: {e}")
        return False

def test_avatar_components():
    """Test AI Avatar components"""
    
    print("\n🧪 Testing AI Avatar components...")
    
    try:
        from src.speech.azure_speech import AzureSpeechService
        print("✅ AzureSpeechService imported successfully")
        
        speech_service = AzureSpeechService()
        connection_ok = speech_service.test_connection()
        
        if connection_ok:
            print("✅ Azure Speech Service connection test passed")
        else:
            print("❌ Azure Speech Service connection test failed")
            
        return connection_ok
        
    except Exception as e:
        print(f"❌ Error testing avatar components: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AI Avatar - Azure Speech Services Test")
    print("=" * 50)
    
    # Test environment configuration
    print("\n📋 Testing environment configuration...")
    env_ok = test_speech_services()
    
    # Test avatar components
    if env_ok:
        component_ok = test_avatar_components()
    else:
        component_ok = False
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    print(f"Environment Configuration: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Avatar Components: {'✅ PASS' if component_ok else '❌ FAIL'}")
    
    if env_ok and component_ok:
        print("\n🎉 All tests passed! Your AI Avatar setup is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        print("\n💡 Next steps:")
        if not env_ok:
            print("   1. Copy .env.example to .env")
            print("   2. Add your Azure Speech Services key and region")
        if not component_ok:
            print("   3. Ensure all dependencies are installed: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
