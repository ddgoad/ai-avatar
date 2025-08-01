/**
 * Avatar WebRTC Manager
 * 
 * Implementation based on Azure official samples for real-time avatar video streaming.
 * Reference: https://github.com/Azure-Samples/cognitive-services-speech-sdk/tree/master/samples/js/browser/avatar
 */

class AvatarManager {
    constructor() {
        this.avatarSynthesizer = null;
        this.peerConnection = null;
        this.peerConnectionDataChannel = null;
        this.sessionActive = false;
        this.isConnecting = false;
        this.iceGatheringDone = false;
        this.lastSpeakTime = null;
        
        // Configuration
        this.cogSvcRegion = null;
        this.cogSvcSubKey = null;
        this.avatarConfig = {
            character: 'lisa',
            style: 'graceful-sitting',
            voice: 'en-US-JennyNeural',
            background: 'solid-white'
        };
        
        console.log('Avatar Manager initialized (WebRTC-based)');
    }
    
    /**
     * Initialize Azure Speech SDK configuration
     */
    async initializeSpeechConfig() {
        try {
            // Get credentials from server (these would be passed from backend)
            const response = await fetch('/api/avatar/config');
            const data = await response.json();
            
            if (response.ok && data.current_settings) {
                this.avatarConfig = { ...this.avatarConfig, ...data.current_settings };
                console.log('Avatar configuration loaded:', this.avatarConfig);
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Failed to initialize speech config:', error);
            return false;
        }
    }
    
    /**
     * Connect to avatar service and start session (based on Azure samples)
     */
    async connectAvatar() {
        if (this.isConnecting || this.sessionActive) {
            console.log('Avatar already connecting or active');
            return { success: false, error: 'Already connecting or active' };
        }
        
        try {
            this.isConnecting = true;
            
            // Initialize configuration
            const configLoaded = await this.initializeSpeechConfig();
            if (!configLoaded) {
                throw new Error('Failed to load avatar configuration');
            }
            
            console.log('Starting avatar connection...');
            
            // Get ICE token for WebRTC
            const iceResponse = await fetch('/api/avatar/ice-token');
            const iceData = await iceResponse.json();
            
            if (!iceResponse.ok || !iceData.success) {
                throw new Error(iceData.error || 'Failed to get ICE token');
            }
            
            // Setup WebRTC with ICE servers
            await this.setupWebRTC(
                iceData.ice_servers[0].urls[0],
                iceData.ice_servers[0].username,
                iceData.ice_servers[0].credential
            );
            
            return { success: true };
            
        } catch (error) {
            console.error('Avatar connection failed:', error);
            this.isConnecting = false;
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Setup WebRTC connection (based on Azure samples)
     */
    async setupWebRTC(iceServerUrl, iceServerUsername, iceServerCredential) {
        try {
            // Create WebRTC peer connection
            this.peerConnection = new RTCPeerConnection({
                iceServers: [{
                    urls: [iceServerUrl],
                    username: iceServerUsername,
                    credential: iceServerCredential
                }],
                iceTransportPolicy: 'relay'
            });
            
            // Handle incoming video stream
            this.peerConnection.ontrack = (event) => {
                if (event.track.kind === 'video') {
                    const videoElement = document.createElement('video');
                    videoElement.id = 'avatarVideo';
                    videoElement.srcObject = event.streams[0];
                    videoElement.autoplay = true;
                    videoElement.playsInline = true;
                    videoElement.controls = false;
                    videoElement.muted = false; // Avatar should have audio
                    
                    videoElement.onplaying = () => {
                        console.log('Avatar video stream connected');
                        
                        // Replace any existing video
                        const remoteVideoDiv = document.getElementById('avatar-video-container');
                        if (remoteVideoDiv) {
                            // Clear existing videos
                            remoteVideoDiv.innerHTML = '';
                            
                            // Style the video element
                            videoElement.style.width = '100%';
                            videoElement.style.height = 'auto';
                            videoElement.style.maxWidth = '960px';
                            
                            remoteVideoDiv.appendChild(videoElement);
                        }
                    };
                } else if (event.track.kind === 'audio') {
                    // Handle audio track
                    const audioElement = document.createElement('audio');
                    audioElement.srcObject = event.streams[0];
                    audioElement.autoplay = true;
                    audioElement.addEventListener('loadeddata', () => {
                        audioElement.play();
                    });
                    
                    console.log('Avatar audio stream connected');
                }
            };
            
            // Listen to data channel for avatar events
            this.peerConnection.addEventListener('datachannel', (event) => {
                this.peerConnectionDataChannel = event.channel;
                this.peerConnectionDataChannel.onmessage = (e) => {
                    console.log('Avatar event received:', e.data);
                    
                    if (e.data.includes('EVENT_TYPE_SWITCH_TO_IDLE')) {
                        this.onAvatarIdle();
                    } else if (e.data.includes('EVENT_TYPE_SPEAKING_STARTED')) {
                        this.onAvatarSpeaking();
                    }
                };
            });
            
            // Create data channel (required for Azure Avatar)
            const dataChannel = this.peerConnection.createDataChannel('eventChannel');
            
            // Handle connection state changes
            this.peerConnection.oniceconnectionstatechange = () => {
                console.log('WebRTC connection state:', this.peerConnection.iceConnectionState);
                
                if (this.peerConnection.iceConnectionState === 'connected') {
                    this.sessionActive = true;
                    this.isConnecting = false;
                    this.onSessionConnected();
                } else if (this.peerConnection.iceConnectionState === 'disconnected') {
                    this.onSessionDisconnected();
                } else if (this.peerConnection.iceConnectionState === 'failed') {
                    this.onSessionFailed();
                }
            };
            
            // Offer to receive video and audio
            this.peerConnection.addTransceiver('video', { direction: 'sendrecv' });
            this.peerConnection.addTransceiver('audio', { direction: 'sendrecv' });
            
            // Create offer and wait for ICE gathering
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            
            // Wait for ICE gathering to complete
            await this.waitForIceGathering();
            
            // Create avatar session on server
            const sessionResponse = await fetch('/api/avatar/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    avatar_config: this.avatarConfig,
                    sdp: this.peerConnection.localDescription
                })
            });
            
            const sessionData = await sessionResponse.json();
            if (!sessionResponse.ok || !sessionData.success) {
                throw new Error(sessionData.error || 'Failed to create avatar session');
            }
            
            console.log('Avatar session created successfully');
            
        } catch (error) {
            console.error('WebRTC setup failed:', error);
            this.isConnecting = false;
            throw error;
        }
    }
    
    /**
     * Wait for ICE gathering to complete
     */
    waitForIceGathering() {
        return new Promise((resolve) => {
            if (this.peerConnection.iceGatheringState === 'complete') {
                resolve();
                return;
            }
            
            const checkState = () => {
                if (this.peerConnection.iceGatheringState === 'complete') {
                    this.peerConnection.removeEventListener('icegatheringstatechange', checkState);
                    resolve();
                }
            };
            
            this.peerConnection.addEventListener('icegatheringstatechange', checkState);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                this.peerConnection.removeEventListener('icegatheringstatechange', checkState);
                resolve();
            }, 10000);
        });
    }
    
    /**
     * Send text to avatar for speech synthesis (based on Azure samples)
     */
    async speak(text) {
        if (!this.sessionActive) {
            console.error('Avatar session not active');
            return { success: false, error: 'Avatar session not active' };
        }
        
        try {
            console.log('Sending text to avatar:', text);
            
            const response = await fetch('/api/avatar/speak', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.lastSpeakTime = new Date();
                console.log('Avatar speech synthesis completed');
                return result;
            } else {
                console.error('Avatar speak failed:', result.error);
                return { success: false, error: result.error };
            }
            
        } catch (error) {
            console.error('Avatar speak error:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Disconnect from avatar service
     */
    async disconnect() {
        try {
            console.log('Disconnecting avatar session...');
            
            // Close avatar session on server
            if (this.sessionActive) {
                const response = await fetch('/api/avatar/session', {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    console.log('Avatar session closed on server');
                }
            }
            
            // Close WebRTC connection
            if (this.peerConnection) {
                this.peerConnection.close();
                this.peerConnection = null;
            }
            
            this.sessionActive = false;
            this.isConnecting = false;
            this.peerConnectionDataChannel = null;
            
            // Clear video element
            const videoContainer = document.getElementById('avatar-video-container');
            if (videoContainer) {
                videoContainer.innerHTML = '';
            }
            
            this.onSessionDisconnected();
            
        } catch (error) {
            console.error('Error disconnecting avatar:', error);
        }
    }
    
    /**
     * Update avatar configuration
     */
    async updateConfig(newConfig) {
        try {
            this.avatarConfig = { ...this.avatarConfig, ...newConfig };
            
            const response = await fetch('/api/avatar/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.avatarConfig)
            });
            
            if (response.ok) {
                console.log('Avatar configuration updated');
                return true;
            } else {
                console.error('Failed to update avatar configuration');
                return false;
            }
            
        } catch (error) {
            console.error('Error updating avatar config:', error);
            return false;
        }
    }
    
    // Event handlers that can be overridden
    onSessionConnected() {
        console.log('Avatar session connected');
        // Enable UI controls
        const startButton = document.getElementById('start-avatar');
        const stopButton = document.getElementById('stop-avatar');
        
        if (startButton) startButton.disabled = true;
        if (stopButton) stopButton.disabled = false;
        
        // Show status
        this.updateStatus('Connected - Ready to speak');
    }
    
    onSessionDisconnected() {
        console.log('Avatar session disconnected');
        // Update UI controls
        const startButton = document.getElementById('start-avatar');
        const stopButton = document.getElementById('stop-avatar');
        
        if (startButton) startButton.disabled = false;
        if (stopButton) stopButton.disabled = true;
        
        // Show status
        this.updateStatus('Disconnected');
    }
    
    onSessionFailed() {
        console.log('Avatar session failed');
        this.sessionActive = false;
        this.isConnecting = false;
        this.updateStatus('Connection failed');
        this.onSessionDisconnected();
    }
    
    onAvatarSpeaking() {
        console.log('Avatar started speaking');
        this.updateStatus('Speaking...');
    }
    
    onAvatarIdle() {
        console.log('Avatar finished speaking');
        this.updateStatus('Ready to speak');
    }
    
    updateStatus(message) {
        const statusElement = document.getElementById('avatar-status');
        if (statusElement) {
            statusElement.textContent = message;
        }
    }
    
    // Public methods for integration
    isActive() {
        return this.sessionActive;
    }
    
    isConnected() {
        return this.sessionActive;
    }
}

// Global avatar manager instance
window.avatarManager = new AvatarManager();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AvatarManager;
}
