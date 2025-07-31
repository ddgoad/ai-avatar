// AI Avatar JavaScript

class AvatarApp {
    constructor() {
        this.form = document.getElementById('avatarForm');
        this.generateBtn = document.getElementById('generateBtn');
        this.statusDiv = document.getElementById('status');
        this.audioContainer = document.getElementById('audioContainer');
        this.videoContainer = document.getElementById('videoContainer');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.videoPlayer = document.getElementById('videoPlayer');
        this.avatarContainer = document.getElementById('avatarContainer');
        
        this.initializeEventListeners();
        this.loadConfiguration();
    }
    
    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateAvatarSpeech();
        });
        
        // Character change handler
        document.getElementById('character').addEventListener('change', () => {
            this.updateAvailableStyles();
        });
    }
    
    async loadConfiguration() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.success) {
                this.populateFormWithConfig(data.config);
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
        }
        
        // Load available avatars and voices
        await this.loadAvailableOptions();
    }
    
    async loadAvailableOptions() {
        try {
            // Load avatars
            const avatarsResponse = await fetch('/api/avatars');
            const avatarsData = await avatarsResponse.json();
            
            if (avatarsData.success) {
                this.populateCharacterOptions(avatarsData.avatars.characters);
                this.updateAvailableStyles();
            }
            
            // Load voices
            const voicesResponse = await fetch('/api/voices');
            const voicesData = await voicesResponse.json();
            
            if (voicesData.success) {
                this.populateVoiceOptions(voicesData.voices);
            }
        } catch (error) {
            console.error('Error loading options:', error);
        }
    }
    
    populateCharacterOptions(characters) {
        const characterSelect = document.getElementById('character');
        characterSelect.innerHTML = '';
        
        for (const [key, character] of Object.entries(characters)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = `${character.name} (${character.description})`;
            characterSelect.appendChild(option);
        }
        
        this.availableCharacters = characters;
    }
    
    populateVoiceOptions(voices) {
        const voiceSelect = document.getElementById('voice');
        voiceSelect.innerHTML = '';
        
        // Filter for English voices and sort by locale
        const englishVoices = voices.filter(voice => 
            voice.locale.startsWith('en-') && 
            voice.voice_type === 'Neural'
        );
        
        englishVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = `${voice.display_name} (${voice.locale})`;
            voiceSelect.appendChild(option);
        });
    }
    
    updateAvailableStyles() {
        const characterSelect = document.getElementById('character');
        const styleSelect = document.getElementById('style');
        const selectedCharacter = characterSelect.value;
        
        if (this.availableCharacters && this.availableCharacters[selectedCharacter]) {
            const styles = this.availableCharacters[selectedCharacter].styles;
            styleSelect.innerHTML = '';
            
            styles.forEach(style => {
                const option = document.createElement('option');
                option.value = style;
                option.textContent = this.formatStyleName(style);
                styleSelect.appendChild(option);
            });
        }
    }
    
    formatStyleName(style) {
        return style.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
    populateFormWithConfig(config) {
        document.getElementById('character').value = config.character;
        document.getElementById('style').value = config.style;
        document.getElementById('voice').value = config.voice;
    }
    
    async generateAvatarSpeech() {
        const formData = new FormData(this.form);
        const data = {
            text: formData.get('text'),
            character: formData.get('character'),
            style: formData.get('style'),
            voice: formData.get('voice')
        };
        
        // Validate input
        if (!data.text.trim()) {
            this.showStatus('Please enter some text to synthesize.', 'warning');
            return;
        }
        
        // Show loading state
        this.setLoadingState(true);
        this.showStatus('Generating avatar speech...', 'info', true);
        
        try {
            const response = await fetch('/api/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.handleSuccess(result);
            } else {
                this.handleError(result.error);
            }
            
        } catch (error) {
            console.error('Error generating speech:', error);
            this.handleError('Network error occurred. Please try again.');
        }
        
        this.setLoadingState(false);
    }
    
    handleSuccess(result) {
        this.showStatus(`Successfully generated speech for ${result.character} (${result.style})`, 'success');
        
        // Show audio player
        if (result.audio_url) {
            this.audioPlayer.src = result.audio_url;
            this.audioContainer.classList.remove('d-none');
            this.audioContainer.classList.add('fade-in');
        }
        
        // Show video player if available
        if (result.video_url) {
            this.videoPlayer.src = result.video_url;
            this.videoContainer.classList.remove('d-none');
            this.videoContainer.classList.add('fade-in');
        }
        
        // Update avatar container
        this.updateAvatarDisplay(result);
    }
    
    updateAvatarDisplay(result) {
        const placeholder = this.avatarContainer.querySelector('.avatar-placeholder');
        if (placeholder) {
            placeholder.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                    <h5>Avatar Speech Generated!</h5>
                    <p class="text-muted">Character: ${result.character}</p>
                    <p class="text-muted">Style: ${result.style}</p>
                    <p class="text-muted">Voice: ${result.voice}</p>
                </div>
            `;
            placeholder.classList.add('fade-in');
        }
    }
    
    handleError(error) {
        this.showStatus(`Error: ${error}`, 'danger');
    }
    
    setLoadingState(loading) {
        const spinner = this.generateBtn.querySelector('.spinner-border');
        const btnText = loading ? 'Generating...' : 'Generate Avatar Speech';
        
        this.generateBtn.disabled = loading;
        spinner.classList.toggle('d-none', !loading);
        
        // Update button text (preserve spinner)
        const textNode = Array.from(this.generateBtn.childNodes)
            .find(node => node.nodeType === Node.TEXT_NODE);
        if (textNode) {
            textNode.textContent = btnText;
        } else {
            this.generateBtn.appendChild(document.createTextNode(btnText));
        }
    }
    
    showStatus(message, type = 'info', pulse = false) {
        this.statusDiv.className = `alert alert-${type}`;
        this.statusDiv.textContent = message;
        
        if (pulse) {
            this.statusDiv.classList.add('status-generating');
        } else {
            this.statusDiv.classList.remove('status-generating');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AvatarApp();
});

// Utility functions
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function showToast(message, type = 'info') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}
