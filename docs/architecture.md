# Architecture

VoiceTranslate runs as three coordinated local processes:
1. Enrollment service (full-screen UI and data capture)
2. Outgoing translation pipeline (mic to virtual mic)
3. Incoming caption pipeline (loopback to overlay and optional speaker output)
