/**
 * AI Avatar Application JavaScript
 * Implementation exactly as specified in the Technical Design Document
 * 
 * Includes all required classes:
 * - InputManager: Handle text/voice input modes
 * - ChatInterface: Manage conversations and UI updates
 * - AudioRecorder: WebRTC audio capture with visualization
 * - AvatarPlayer: Video playback and management
 */

// Enhanced Input Manager
class InputManager {
    constructor() {
        this.audioRecorder = new AudioRecorder();
        this.inputMode = 'text'; // 'text' or 'voice'
        this.isRecording = false;
        
        console.log('InputManager initialized');
    }
    
    setInputMode(mode) {
        this.inputMode = mode;
        this.updateUI();
        console.log(`Input mode changed to: ${mode}`);
    }
    
    async handleInput() {
        if (this.inputMode === 'voice') {
            return await this.handleVoiceInput();
        } else {
            return this.handleTextInput();
        }
    }
    
    async handleVoiceInput() {
        if (!this.isRecording) {
            try {
                await this.audioRecorder.startRecording();
                this.isRecording = true;
                this.updateRecordingUI(true);
                return null; // No input yet, just started recording
            } catch (error) {
                console.error('Failed to start recording:', error);
                this.showError('Failed to start recording. Please check microphone permissions.');
                return null;
            }
        } else {
            try {
                const audioBlob = await this.audioRecorder.stopRecording();
                this.isRecording = false;
                this.updateRecordingUI(false);
                return { type: 'voice', data: audioBlob };
            } catch (error) {
                console.error('Failed to stop recording:', error);
                this.showError('Failed to stop recording.');
                this.isRecording = false;
                this.updateRecordingUI(false);
                return null;
            }
        }
    }
    
    handleTextInput() {
        const textInput = document.getElementById('text-input');
        const text = textInput.value.trim();
        if (text) {
            textInput.value = '';
            return { type: 'text', data: text };
        }
        return null;
    }
    
    updateUI() {
        const voiceControls = document.getElementById('voice-controls');
        const textControls = document.getElementById('text-controls');
        
        if (this.inputMode === 'voice') {
            if (voiceControls) voiceControls.style.display = 'block';
            if (textControls) textControls.style.display = 'none';
        } else {
            if (voiceControls) voiceControls.style.display = 'none';
            if (textControls) textControls.style.display = 'block';
        }
    }
    
    updateRecordingUI(isRecording) {
        const recordButton = document.getElementById('record-button');
        const recordText = document.querySelector('.record-text');
        
        if (recordButton && recordText) {
            recordText.textContent = isRecording ? 'Stop Recording' : 'Start Recording';
            recordButton.classList.toggle('recording', isRecording);
        }
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    }
}

// Enhanced Chat Interface
class ChatInterface {
    constructor() {
        this.inputManager = new InputManager();
        this.avatarPlayer = new AvatarPlayer(document.getElementById('avatar-video'));
        this.conversationHistory = [];
        this.selectedModel = 'gpt4o';
        this.avatarSettings = {
            character: 'lisa',
            style: 'graceful-sitting',
            voice: 'en-US-JennyNeural',
            background: 'solid-white',
            gesture: null,
            video_quality: 'high'
        };
        
        this.initializeAvatarOptions();
        console.log('ChatInterface initialized');
    }
    
    async initializeAvatarOptions() {
        try {
            const response = await fetch('/api/avatar/config');
            if (response.ok) {
                const data = await response.json();
                this.populateAvatarControls(data.available_options);
            } else {
                console.warn('Failed to load avatar options, using defaults');
                this.populateDefaultAvatarControls();
            }
        } catch (error) {
            console.error('Failed to load avatar options:', error);
            this.populateDefaultAvatarControls();
        }
    }
    
    populateAvatarControls(options) {
        if (!options) {
            this.populateDefaultAvatarControls();
            return;
        }
        
        // Populate character selector
        const characterSelect = document.getElementById('avatar-character');
        if (characterSelect && options.characters) {
            characterSelect.innerHTML = '';
            options.characters.forEach(char => {
                const option = document.createElement('option');
                option.value = char.id;
                option.textContent = char.name;
                option.title = char.description;
                characterSelect.appendChild(option);
            });
        }
        
        // Populate style selector
        const styleSelect = document.getElementById('avatar-style');
        if (styleSelect && options.styles) {
            styleSelect.innerHTML = '';
            options.styles.forEach(style => {
                const option = document.createElement('option');
                option.value = style.id;
                option.textContent = style.name;
                option.title = style.description;
                styleSelect.appendChild(option);
            });
        }
        
        // Populate voice selector
        const voiceSelect = document.getElementById('avatar-voice');
        if (voiceSelect && options.voices) {
            voiceSelect.innerHTML = '';
            options.voices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.id;
                option.textContent = `${voice.name} (${voice.gender})`;
                voiceSelect.appendChild(option);
            });
        }
        
        // Populate background selector
        const backgroundSelect = document.getElementById('avatar-background');
        if (backgroundSelect && options.backgrounds) {
            backgroundSelect.innerHTML = '';
            options.backgrounds.forEach(bg => {
                const option = document.createElement('option');
                option.value = bg.id;
                option.textContent = bg.name;
                backgroundSelect.appendChild(option);
            });
        }
        
        // Populate gesture selector
        const gestureSelect = document.getElementById('avatar-gesture');
        if (gestureSelect && options.gestures) {
            gestureSelect.innerHTML = '<option value="">No Gesture</option>';
            options.gestures.forEach(gesture => {
                const option = document.createElement('option');
                option.value = gesture.id;
                option.textContent = gesture.name;
                option.title = gesture.description;
                gestureSelect.appendChild(option);
            });
        }
        
        // Set up event listeners for avatar settings
        this.setupAvatarSettingsListeners();
    }
    
    populateDefaultAvatarControls() {
        // Fallback when API is not available
        const defaultOptions = {
            characters: [
                {id: 'lisa', name: 'Lisa', description: 'Professional female avatar'},
                {id: 'mark', name: 'Mark', description: 'Professional male avatar'},
                {id: 'anna', name: 'Anna', description: 'Casual female avatar'}
            ],
            styles: [
                {id: 'graceful-sitting', name: 'Graceful Sitting', description: 'Elegant seated pose'},
                {id: 'standing', name: 'Standing', description: 'Professional standing pose'}
            ],
            voices: [
                {id: 'en-US-JennyNeural', name: 'Jenny (US)', gender: 'Female'},
                {id: 'en-US-DavisNeural', name: 'Davis (US)', gender: 'Male'}
            ]
        };
        
        this.populateAvatarControls(defaultOptions);
    }
    
    setupAvatarSettingsListeners() {
        const selectors = [
            'avatar-character', 'avatar-style', 'avatar-voice', 
            'avatar-background', 'avatar-gesture', 'video-quality'
        ];
        
        selectors.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', (e) => {
                    const setting = id.replace('avatar-', '').replace('video-', '');
                    this.avatarSettings[setting] = e.target.value || null;
                    this.updateAvatarPreview();
                });
            }
        });
    }
    
    async updateAvatarPreview() {
        const previewContainer = document.getElementById('avatar-preview');
        if (previewContainer) {
            previewContainer.innerHTML = `
                <div class="avatar-preview-info">
                    <h4>Avatar Preview</h4>
                    <p><strong>Character:</strong> ${this.avatarSettings.character}</p>
                    <p><strong>Style:</strong> ${this.avatarSettings.style}</p>
                    <p><strong>Voice:</strong> ${this.avatarSettings.voice}</p>
                    <p><strong>Background:</strong> ${this.avatarSettings.background}</p>
                </div>
            `;
        }
    }
    
    async sendMessage() {
        const input = await this.inputManager.handleInput();
        if (!input) return;
        
        // Add user message to chat
        this.addMessageToChat('user', input.data, input.type);
        
        // Show loading indicator
        this.showLoadingIndicator();
        
        try {
            // Send to backend
            const response = await this.sendToBackend(input, this.selectedModel);
            
            if (response.success) {
                // Add AI response to chat
                this.addMessageToChat('assistant', response.text, 'text');
                
                // Play avatar video if available
                if (response.video_url) {
                    console.log('Playing avatar video for response:', response.video_url);
                    try {
                        await this.avatarPlayer.playAvatarVideo(response.video_url);
                        console.log('Avatar video played successfully');
                    } catch (videoError) {
                        console.error('Video playback failed:', videoError);
                        this.showError(`Video playback failed: ${videoError.message}. The text response is still available above.`);
                    }
                } else {
                    console.log('No video URL in response');
                }
                
                // Update conversation history - use the transcribed text for voice input
                const userContent = response.user_input_text || 
                    (input.type === 'text' ? input.data : 'Voice message');
                
                this.conversationHistory.push(
                    { role: 'user', content: userContent },
                    { role: 'assistant', content: response.text }
                );
            } else {
                this.showError(response.error || 'Failed to get response');
            }
            
        } catch (error) {
            console.error('Send message error:', error);
            this.showError('Failed to get response: ' + error.message);
        } finally {
            this.hideLoadingIndicator();
        }
    }
    
    addMessageToChat(sender, content, type) {
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const typeIcon = type === 'voice' ? '🎤' : '💬';
        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="sender">${sender === 'user' ? 'You' : 'Avatar'}</span>
                <span class="type-icon">${typeIcon}</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${this.escapeHtml(content)}</div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    async sendToBackend(input, model) {
        const formData = new FormData();
        
        if (input.type === 'voice') {
            formData.append('audio', input.data);
            formData.append('input_type', 'voice');
        } else {
            formData.append('text', input.data);
            formData.append('input_type', 'text');
        }
        
        formData.append('model', model);
        formData.append('conversation_history', JSON.stringify(this.conversationHistory));
        formData.append('avatar_settings', JSON.stringify(this.avatarSettings));
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    setModel(model) {
        this.selectedModel = model;
        const indicator = document.getElementById('model-indicator');
        if (indicator) {
            indicator.textContent = model.toUpperCase();
        }
    }
    
    showLoadingIndicator() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }
    
    hideLoadingIndicator() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    }
    
    async clearConversation() {
        try {
            const response = await fetch('/api/conversation', { method: 'DELETE' });
            if (response.ok) {
                this.conversationHistory = [];
                const chatContainer = document.getElementById('chat-container');
                if (chatContainer) {
                    chatContainer.innerHTML = '';
                }
            }
        } catch (error) {
            console.error('Failed to clear conversation:', error);
            this.showError('Failed to clear conversation');
        }
    }
    
    async exportConversation() {
        try {
            const response = await fetch('/api/export-conversation');
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'conversation_export.json';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('Failed to export conversation:', error);
            this.showError('Failed to export conversation');
        }
    }
}

// WebRTC Audio Capture with Enhanced Features
class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        
        console.log('AudioRecorder initialized');
    }
    
    async startRecording() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });
            
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            this.isRecording = true;
            
            this.mediaRecorder.addEventListener('dataavailable', (event) => {
                this.audioChunks.push(event.data);
            });
            
            this.mediaRecorder.start();
            this.startVisualization();
            
            console.log('Recording started');
        } catch (error) {
            console.error('Failed to start recording:', error);
            throw error;
        }
    }
    
    stopRecording() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder || !this.isRecording) {
                reject(new Error('No active recording'));
                return;
            }
            
            this.mediaRecorder.addEventListener('stop', () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.stopVisualization();
                this.cleanup();
                console.log('Recording stopped');
                resolve(audioBlob);
            });
            
            this.mediaRecorder.stop();
            this.isRecording = false;
        });
    }
    
    startVisualization() {
        try {
            const canvas = document.getElementById('audio-visualizer');
            if (!canvas) return;
            
            const audioContext = new AudioContext();
            const analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaStreamSource(this.stream);
            source.connect(analyser);
            
            const ctx = canvas.getContext('2d');
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            
            const visualize = () => {
                if (this.isRecording) {
                    requestAnimationFrame(visualize);
                    
                    const bufferLength = analyser.frequencyBinCount;
                    const dataArray = new Uint8Array(bufferLength);
                    analyser.getByteFrequencyData(dataArray);
                    
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    const barWidth = (canvas.width / bufferLength) * 2.5;
                    let barHeight;
                    let x = 0;
                    
                    for (let i = 0; i < bufferLength; i++) {
                        barHeight = dataArray[i] / 2;
                        
                        ctx.fillStyle = `rgb(50, ${barHeight + 100}, 50)`;
                        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                        
                        x += barWidth + 1;
                    }
                }
            };
            
            visualize();
        } catch (error) {
            console.error('Visualization error:', error);
        }
    }
    
    stopVisualization() {
        const canvas = document.getElementById('audio-visualizer');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }
    
    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.isRecording = false;
    }
}

// Avatar Video Player with Enhanced Features
class AvatarPlayer {
    constructor(videoElement) {
        this.video = videoElement;
        this.currentVideoUrl = null;
        
        if (this.video) {
            this.setupEventListeners();
        }
        
        console.log('AvatarPlayer initialized');
    }
    
    setupEventListeners() {
        this.video.addEventListener('loadstart', () => {
            this.showVideoLoading(true);
        });
        
        this.video.addEventListener('canplay', () => {
            this.showVideoLoading(false);
        });
        
        this.video.addEventListener('ended', () => {
            this.onVideoEnded();
        });
        
        this.video.addEventListener('error', (e) => {
            console.error('Video error:', e);
            this.showVideoLoading(false);
        });
    }
    
    async playAvatarVideo(videoUrl) {
        if (!this.video) return;
        
        try {
            this.showVideoLoading(true);
            
            // Clean up previous video URL
            if (this.currentVideoUrl) {
                URL.revokeObjectURL(this.currentVideoUrl);
            }
            
            console.log('Starting video fetch from:', videoUrl);
            
            // Use GET request with manual redirect handling
            const response = await fetch(videoUrl, {
                method: 'GET',
                redirect: 'manual'  // Don't follow redirects automatically
            });
            
            console.log('Response status:', response.status);
            console.log('Response headers:', [...response.headers.entries()]);
            
            if (response.status === 302 || response.status === 301) {
                // Get the redirect location
                const redirectUrl = response.headers.get('Location');
                console.log('Redirect URL found:', redirectUrl);
                
                if (!redirectUrl) {
                    throw new Error('Redirect URL not found in response headers');
                }
                
                // Fetch the video directly from Azure Blob Storage
                console.log('Fetching video blob from Azure Storage:', redirectUrl);
                const blobResponse = await fetch(redirectUrl, {
                    method: 'GET',
                    mode: 'cors',
                    credentials: 'omit',
                    headers: {
                        'Accept': 'video/*'
                    }
                });
                
                if (!blobResponse.ok) {
                    throw new Error(`Failed to fetch video blob from Azure: ${blobResponse.status} ${blobResponse.statusText}`);
                }
                
                const contentType = blobResponse.headers.get('Content-Type');
                console.log('Content-Type from Azure:', contentType);
                
                const videoBlob = await blobResponse.blob();
                console.log('Video blob loaded, size:', videoBlob.size, 'type:', videoBlob.type);
                
                // Create blob URL and set video source
                this.currentVideoUrl = URL.createObjectURL(videoBlob);
                this.video.src = this.currentVideoUrl;
                
            } else if (response.status === 200) {
                // Direct response, fetch the full content
                console.log('Direct response, fetching video content');
                const videoBlob = await response.blob();
                console.log('Video blob loaded directly, size:', videoBlob.size, 'type:', videoBlob.type);
                
                this.currentVideoUrl = URL.createObjectURL(videoBlob);
                this.video.src = this.currentVideoUrl;
                
            } else {
                throw new Error(`Unexpected response status: ${response.status} ${response.statusText}`);
            }
            
            // Wait for video to load and play
            return new Promise((resolve, reject) => {
                let resolved = false;
                
                const handleLoadedData = () => {
                    console.log('Video loaded successfully');
                    this.showVideoLoading(false);
                    if (!resolved) {
                        resolved = true;
                        this.video.play().then(resolve).catch(reject);
                    }
                };
                
                const handleCanPlay = () => {
                    console.log('Video can play');
                    this.showVideoLoading(false);
                    if (!resolved) {
                        resolved = true;
                        this.video.play().then(resolve).catch(reject);
                    }
                };
                
                const handleError = (e) => {
                    console.error('Video element error:', e);
                    this.showVideoLoading(false);
                    if (!resolved) {
                        resolved = true;
                        reject(new Error(`Video element failed to load: ${e.message || 'Unknown error'}`));
                    }
                };
                
                const handleLoadStart = () => {
                    console.log('Video load started');
                };
                
                // Set up event listeners
                this.video.addEventListener('loadeddata', handleLoadedData, { once: true });
                this.video.addEventListener('canplay', handleCanPlay, { once: true });
                this.video.addEventListener('error', handleError, { once: true });
                this.video.addEventListener('loadstart', handleLoadStart, { once: true });
                
                // Start loading
                this.video.load();
                
                // Timeout after 30 seconds
                setTimeout(() => {
                    if (!resolved) {
                        resolved = true;
                        reject(new Error('Video loading timeout after 30 seconds'));
                    }
                }, 30000);
            });
            
        } catch (error) {
            console.error('Failed to play avatar video:', error);
            this.showVideoLoading(false);
            
            // Show user-friendly error with more details
            const errorDiv = document.getElementById('error-message');
            if (errorDiv) {
                errorDiv.textContent = `Failed to load avatar video: ${error.message}`;
                errorDiv.style.display = 'block';
                setTimeout(() => {
                    errorDiv.style.display = 'none';
                }, 8000);
            }
            
            throw error; // Re-throw for calling code
        }
    }
    
    async playAvatarResponse(videoBlob) {
        if (!this.video) return;
        
        try {
            // Clean up previous video URL
            if (this.currentVideoUrl) {
                URL.revokeObjectURL(this.currentVideoUrl);
            }
            
            this.currentVideoUrl = URL.createObjectURL(videoBlob);
            this.video.src = this.currentVideoUrl;
            
            await this.video.play();
            
            return new Promise((resolve) => {
                this.video.addEventListener('ended', resolve, { once: true });
            });
        } catch (error) {
            console.error('Failed to play avatar response:', error);
            this.showVideoLoading(false);
        }
    }
    
    showVideoLoading(isLoading) {
        const loadingOverlay = document.getElementById('video-loading');
        if (loadingOverlay) {
            loadingOverlay.style.display = isLoading ? 'flex' : 'none';
        }
    }
    
    onVideoEnded() {
        // Clean up and prepare for next video
        if (this.currentVideoUrl) {
            URL.revokeObjectURL(this.currentVideoUrl);
            this.currentVideoUrl = null;
        }
        console.log('Avatar video ended');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Avatar App initializing...');
    
    const chatInterface = new ChatInterface();
    
    // Set up event listeners
    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.addEventListener('click', () => {
            chatInterface.sendMessage();
        });
    }
    
    const textInput = document.getElementById('text-input');
    if (textInput) {
        textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatInterface.sendMessage();
            }
        });
    }
    
    const inputModeRadios = document.querySelectorAll('input[name="input-mode"]');
    inputModeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            chatInterface.inputManager.setInputMode(e.target.value);
        });
    });
    
    const modelSelector = document.getElementById('model-selector');
    if (modelSelector) {
        modelSelector.addEventListener('change', (e) => {
            chatInterface.setModel(e.target.value);
        });
    }
    
    const recordButton = document.getElementById('record-button');
    if (recordButton) {
        recordButton.addEventListener('click', () => {
            chatInterface.sendMessage();
        });
    }
    
    const clearButton = document.getElementById('clear-conversation');
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            chatInterface.clearConversation();
        });
    }
    
    const exportButton = document.getElementById('export-conversation');
    if (exportButton) {
        exportButton.addEventListener('click', () => {
            chatInterface.exportConversation();
        });
    }
    
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/logout', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    window.location.href = result.redirect || '/login';
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    }
    
    console.log('AI Avatar App initialized successfully');
});
