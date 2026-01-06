"""
Voice Assistant API endpoints
"""
from fastapi import APIRouter, Depends
from auth import get_current_active_user, User
from voice_assistant import VoiceAssistant
from typing import Dict

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])

# Global voice assistant instance
voice_assistant_instance = None


@router.post("/activate")
async def activate_voice_assistant(
    current_user: User = Depends(get_current_active_user)
) -> Dict:
    """Activate voice assistant"""
    global voice_assistant_instance
    try:
        if voice_assistant_instance is None:
            voice_assistant_instance = VoiceAssistant()
            voice_assistant_instance.start()
            return {
                "success": True,
                "message": "Voice assistant activated. Say 'Hey AutoSense' to begin."
            }
        else:
            return {
                "success": True,
                "message": "Voice assistant is already active."
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/deactivate")
async def deactivate_voice_assistant(
    current_user: User = Depends(get_current_active_user)
) -> Dict:
    """Deactivate voice assistant"""
    global voice_assistant_instance
    try:
        if voice_assistant_instance:
            voice_assistant_instance.stop()
            voice_assistant_instance = None
            return {
                "success": True,
                "message": "Voice assistant deactivated."
            }
        else:
            return {
                "success": True,
                "message": "Voice assistant is not active."
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/status")
async def get_voice_assistant_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict:
    """Get voice assistant status"""
    global voice_assistant_instance
    return {
        "success": True,
        "active": voice_assistant_instance is not None and voice_assistant_instance.is_listening
    }

