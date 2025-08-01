// AI Avatar Chat - Azure Sample Implementation
// Based on Microsoft's official Azure Speech SDK samples

// Global objects
var speechRecognizer
var avatarSynthesizer
var peerConnection
var peerConnectionDataChannel
var messages = []
var messageInitiated = false
var dataSources = []
var sentenceLevelPunctuations = ['.', '?', '!', ':', ';', '。', '？', '！', '：', '；']
var enableDisplayTextAlignmentWithSpeech = true
var enableQuickReply = false
var quickReplies = ['Let me take a look.', 'Let me check.', 'One moment, please.']
var byodDocRegex = new RegExp(/\[doc(\d+)\]/g)
var isSpeaking = false
var isReconnecting = false
var speakingText = ""
var spokenTextQueue = []
var repeatSpeakingSentenceAfterReconnection = true
var sessionActive = false
var userClosedSession = false
var lastInteractionTime = new Date()
var lastSpeakTime
var imgUrl = ""

// Connect to avatar service
function connectAvatar() {
    // Prevent connecting if already active or connecting
    if (sessionActive) {
        console.log('Avatar session already active')
        return
    }
    
    if (isReconnecting && !userClosedSession) {
        // Allow reconnection attempts
        console.log('Attempting to reconnect avatar session...')
    } else {
        // Reset reconnection flag for manual connections
        isReconnecting = false
    }
    
    // Use configuration from window.azureConfig (set during page load)
    const cogSvcRegion = window.azureConfig?.speech_region || 'southeastasia'
    const cogSvcSubKey = window.azureConfig?.speech_key
    
    if (!cogSvcSubKey) {
        alert('Azure Speech API key not configured. Please check server configuration.')
        return
    }

    // Always use standard endpoint (no private endpoint support in simplified UI)
    const speechSynthesisConfig = SpeechSDK.SpeechConfig.fromSubscription(cogSvcSubKey, cogSvcRegion)

    const ttsVoice = document.getElementById('ttsVoice').value
    speechSynthesisConfig.speechSynthesisVoiceName = ttsVoice

    const talkingAvatarCharacter = document.getElementById('talkingAvatarCharacter').value
    const talkingAvatarStyle = document.getElementById('talkingAvatarStyle').value
    const avatarConfig = new SpeechSDK.AvatarConfig(talkingAvatarCharacter, talkingAvatarStyle)
    avatarSynthesizer = new SpeechSDK.AvatarSynthesizer(speechSynthesisConfig, avatarConfig)
    avatarSynthesizer.avatarEventReceived = function (s, e) {
        var offsetMessage = ", offset from session start: " + e.offset / 10000 + "ms."
        if (e.offset === 0) {
            offsetMessage = ""
        }
        console.log("Event received: " + e.description + offsetMessage)
    }

    // Set up speech recognition with Australian English default
    const speechRecognitionConfig = SpeechSDK.SpeechConfig.fromEndpoint(
        new URL(`wss://${cogSvcRegion}.stt.speech.microsoft.com/speech/universal/v2`), 
        cogSvcSubKey
    )
    speechRecognitionConfig.setProperty(SpeechSDK.PropertyId.SpeechServiceConnection_LanguageIdMode, "Continuous")
    
    // Use Australian English as default STT locale
    const sttLocales = [window.azureConfig?.stt_locales || 'en-AU']
    var autoDetectSourceLanguageConfig = SpeechSDK.AutoDetectSourceLanguageConfig.fromLanguages(sttLocales)
    speechRecognizer = SpeechSDK.SpeechRecognizer.FromConfig(speechRecognitionConfig, autoDetectSourceLanguageConfig, SpeechSDK.AudioConfig.fromDefaultMicrophoneInput())

    // Use configured Azure OpenAI settings
    const azureOpenAIEndpoint = window.azureConfig?.openai_endpoint
    const azureOpenAIApiKey = window.azureConfig?.openai_key
    const azureOpenAIDeploymentName = document.getElementById('azureOpenAIDeploymentName').value
    
    if (!azureOpenAIEndpoint || !azureOpenAIApiKey) {
        alert('Azure OpenAI not configured. Please check server configuration.')
        return
    }

    // No On Your Data support in simplified UI
    dataSources = []

    // Only initialize messages once
    if (!messageInitiated) {
        initMessages()
        messageInitiated = true
    }

    document.getElementById('startSession').disabled = true
    document.getElementById('configuration').hidden = true

    const xhr = new XMLHttpRequest()
    xhr.open("GET", `https://${cogSvcRegion}.tts.speech.microsoft.com/cognitiveservices/avatar/relay/token/v1`)
    xhr.setRequestHeader("Ocp-Apim-Subscription-Key", cogSvcSubKey)
    xhr.addEventListener("readystatechange", function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                try {
                    const responseData = JSON.parse(this.responseText)
                    const iceServerUrl = responseData.Urls[0]
                    const iceServerUsername = responseData.Username
                    const iceServerCredential = responseData.Password
                    setupWebRTC(iceServerUrl, iceServerUsername, iceServerCredential)
                } catch (error) {
                    console.error('Failed to parse avatar token response:', error)
                    alert('Failed to initialize avatar connection. Please try again.')
                    document.getElementById('startSession').disabled = false
                    document.getElementById('configuration').hidden = false
                }
            } else {
                console.error('Avatar token request failed:', this.status, this.responseText)
                alert('Failed to get avatar connection token. Please check your Azure Speech credentials.')
                document.getElementById('startSession').disabled = false
                document.getElementById('configuration').hidden = false
            }
        }
    })
    xhr.onerror = function() {
        console.error('Network error during avatar token request')
        alert('Network error during avatar connection. Please check your internet connection.')
        document.getElementById('startSession').disabled = false
        document.getElementById('configuration').hidden = false
    }
    xhr.send()
}

// Disconnect from avatar service
function disconnectAvatar() {
    console.log('[' + (new Date()).toISOString() + '] Disconnecting avatar session...')
    
    // Close avatar synthesizer
    if (avatarSynthesizer !== undefined) {
        avatarSynthesizer.close()
        avatarSynthesizer = undefined
    }

    // Close speech recognizer
    if (speechRecognizer !== undefined) {
        speechRecognizer.stopContinuousRecognitionAsync()
        speechRecognizer.close()
        speechRecognizer = undefined
    }

    // Close WebRTC peer connection
    if (peerConnection !== undefined) {
        console.log('[' + (new Date()).toISOString() + '] Closing WebRTC peer connection...')
        peerConnection.close()
        peerConnection = undefined
    }

    // Clear data channel
    if (peerConnectionDataChannel !== undefined) {
        peerConnectionDataChannel = undefined
    }

    // Reset connection state
    sessionActive = false
    isReconnecting = false
    isSpeaking = false
    
    // Clear video and audio elements
    const remoteVideoDiv = document.getElementById('remoteVideo')
    if (remoteVideoDiv) {
        remoteVideoDiv.innerHTML = ''
    }
    
    console.log('[' + (new Date()).toISOString() + '] Avatar session disconnected successfully')
}

// Setup WebRTC
function setupWebRTC(iceServerUrl, iceServerUsername, iceServerCredential) {
    // Create WebRTC peer connection
    peerConnection = new RTCPeerConnection({
        iceServers: [{
            urls: [iceServerUrl],
            username: iceServerUsername,
            credential: iceServerCredential
        }]
    })

    // Fetch WebRTC video stream and mount it to an HTML video element
    peerConnection.ontrack = function (event) {
        if (event.track.kind === 'audio') {
            let audioElement = document.createElement('audio')
            audioElement.id = 'audioPlayer'
            audioElement.srcObject = event.streams[0]
            audioElement.autoplay = false
            audioElement.addEventListener('loadeddata', () => {
                audioElement.play()
            })

            audioElement.onplaying = () => {
                console.log(`WebRTC ${event.track.kind} channel connected.`)
            }

            // Clean up existing audio element if there is any
            remoteVideoDiv = document.getElementById('remoteVideo')
            for (var i = 0; i < remoteVideoDiv.childNodes.length; i++) {
                if (remoteVideoDiv.childNodes[i].localName === event.track.kind) {
                    remoteVideoDiv.removeChild(remoteVideoDiv.childNodes[i])
                }
            }

            // Append the new audio element
            document.getElementById('remoteVideo').appendChild(audioElement)
        }

        if (event.track.kind === 'video') {
            let videoElement = document.createElement('video')
            videoElement.id = 'videoPlayer'
            videoElement.srcObject = event.streams[0]
            videoElement.autoplay = false
            videoElement.addEventListener('loadeddata', () => {
                videoElement.play()
            })

            videoElement.playsInline = true
            videoElement.style.width = '0.5px'
            document.getElementById('remoteVideo').appendChild(videoElement)

            // Continue speaking if there are unfinished sentences
            if (repeatSpeakingSentenceAfterReconnection) {
                if (speakingText !== '') {
                    speakNext(speakingText, 0, true)
                }
            } else {
                if (spokenTextQueue.length > 0) {
                    speakNext(spokenTextQueue.shift())
                }
            }

            videoElement.onplaying = () => {
                // Clean up existing video element if there is any
                remoteVideoDiv = document.getElementById('remoteVideo')
                for (var i = 0; i < remoteVideoDiv.childNodes.length; i++) {
                    if (remoteVideoDiv.childNodes[i].localName === event.track.kind) {
                        remoteVideoDiv.removeChild(remoteVideoDiv.childNodes[i])
                    }
                }

                // Append the new video element
                videoElement.style.width = '960px'
                document.getElementById('remoteVideo').appendChild(videoElement)

                console.log(`WebRTC ${event.track.kind} channel connected.`)
                document.getElementById('microphone').disabled = false
                document.getElementById('stopSession').disabled = false
                document.getElementById('remoteVideo').style.width = '960px'
                document.getElementById('chatHistory').hidden = false
                document.getElementById('showTypeMessage').disabled = false

                if (document.getElementById('useLocalVideoForIdle').checked) {
                    document.getElementById('localVideo').hidden = true
                    if (lastSpeakTime === undefined) {
                        lastSpeakTime = new Date()
                    }
                }

                isReconnecting = false
                setTimeout(() => { sessionActive = true }, 5000) // Set session active after 5 seconds
            }
        }
    }

    // Listen to data channel, to get the event from the server
    peerConnection.addEventListener("datachannel", event => {
        peerConnectionDataChannel = event.channel
        peerConnectionDataChannel.onmessage = e => {
            let subtitles = document.getElementById('subtitles')
            const webRTCEvent = JSON.parse(e.data)
            if (webRTCEvent.event.eventType === 'EVENT_TYPE_TURN_START' && document.getElementById('showSubtitles').checked) {
                subtitles.hidden = false
                subtitles.innerHTML = speakingText
            } else if (webRTCEvent.event.eventType === 'EVENT_TYPE_SESSION_END' || webRTCEvent.event.eventType === 'EVENT_TYPE_SWITCH_TO_IDLE') {
                subtitles.hidden = true
                if (webRTCEvent.event.eventType === 'EVENT_TYPE_SESSION_END') {
                    if (document.getElementById('autoReconnectAvatar').checked && !userClosedSession && !isReconnecting) {
                        // No longer reconnect when there is no interaction for a while - extended to 30 minutes
                        if (new Date() - lastInteractionTime < 1800000) {
                            // Session disconnected unexpectedly, need reconnect
                            console.log(`[${(new Date()).toISOString()}] The WebSockets got disconnected, need reconnect.`)
                            isReconnecting = true

                            // Remove data channel onmessage callback to avoid duplicatedly triggering reconnect
                            peerConnectionDataChannel.onmessage = null

                            // Release the existing avatar connection
                            if (avatarSynthesizer !== undefined) {
                                avatarSynthesizer.close()
                            }

                            // Setup a new avatar connection
                            connectAvatar()
                        }
                    }
                }
            }

            console.log("[" + (new Date()).toISOString() + "] WebRTC event received: " + e.data)
        }
    })

    // This is a workaround to make sure the data channel listening is working by creating a data channel from the client side
    c = peerConnection.createDataChannel("eventChannel")

    // Make necessary update to the web page when the connection state changes
    peerConnection.oniceconnectionstatechange = e => {
        console.log("WebRTC status: " + peerConnection.iceConnectionState)

        if (peerConnection.iceConnectionState === 'disconnected') {
            if (document.getElementById('useLocalVideoForIdle').checked) {
                document.getElementById('localVideo').hidden = false
                document.getElementById('remoteVideo').style.width = '0.1px'
            }
        }
    }

    // Offer to receive 1 audio, and 1 video track
    peerConnection.addTransceiver('video', { direction: 'sendrecv' })
    peerConnection.addTransceiver('audio', { direction: 'sendrecv' })

    // start avatar, establish WebRTC connection
    avatarSynthesizer.startAvatarAsync(peerConnection).then((r) => {
        if (r.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
            console.log("[" + (new Date()).toISOString() + "] Avatar started. Result ID: " + r.resultId)
        } else {
            console.log("[" + (new Date()).toISOString() + "] Unable to start avatar. Result ID: " + r.resultId)
            if (r.reason === SpeechSDK.ResultReason.Canceled) {
                let cancellationDetails = SpeechSDK.CancellationDetails.fromResult(r)
                if (cancellationDetails.reason === SpeechSDK.CancellationReason.Error) {
                    console.log(cancellationDetails.errorDetails)
                };

                console.log("Unable to start avatar: " + cancellationDetails.errorDetails);
            }
            document.getElementById('startSession').disabled = false;
            document.getElementById('configuration').hidden = false;
        }
    }).catch(
        (error) => {
            console.log("[" + (new Date()).toISOString() + "] Avatar failed to start. Error: " + error)
            document.getElementById('startSession').disabled = false
            document.getElementById('configuration').hidden = false
        }
    )
}

// Initialize messages
function initMessages() {
    messages = []

    if (dataSources.length === 0) {
        let systemPrompt = document.getElementById('prompt').value
        let systemMessage = {
            role: 'system',
            content: systemPrompt
        }
        messages.push(systemMessage)
    }
}

// Set data sources for chat API
function setDataSources(azureCogSearchEndpoint, azureCogSearchApiKey, azureCogSearchIndexName) {
    let dataSource = {
        type: 'AzureCognitiveSearch',
        parameters: {
            endpoint: azureCogSearchEndpoint,
            key: azureCogSearchApiKey,
            indexName: azureCogSearchIndexName,
            semanticConfiguration: '',
            queryType: 'simple',
            fieldsMapping: {
                contentFieldsSeparator: '\n',
                contentFields: ['content'],
                filepathField: null,
                titleField: 'title',
                urlField: null
            },
            inScope: true,
            roleInformation: document.getElementById('prompt').value
        }
    }

    dataSources.push(dataSource)
}

// Do HTML encoding on given text
function htmlEncode(text) {
    const entityMap = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;'
    };

    return String(text).replace(/[&<>"'\/]/g, (match) => entityMap[match])
}

// Speak the given text
function speak(text, endingSilenceMs = 0) {
    if (isSpeaking) {
        spokenTextQueue.push(text)
        return
    }

    speakNext(text, endingSilenceMs)
}

function speakNext(text, endingSilenceMs = 0, skipUpdatingChatHistory = false) {
    let ttsVoice = document.getElementById('ttsVoice').value
    let ssml = `<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'><voice name='${ttsVoice}'><mstts:leadingsilence-exact value='0'/>${htmlEncode(text)}</voice></speak>`
    if (endingSilenceMs > 0) {
        ssml = `<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'><voice name='${ttsVoice}'><mstts:leadingsilence-exact value='0'/>${htmlEncode(text)}<break time='${endingSilenceMs}ms' /></voice></speak>`
    }

    if (enableDisplayTextAlignmentWithSpeech && !skipUpdatingChatHistory) {
        let chatHistoryTextArea = document.getElementById('chatHistory')
        chatHistoryTextArea.innerHTML += text.replace(/\n/g, '<br/>')
        chatHistoryTextArea.scrollTop = chatHistoryTextArea.scrollHeight
    }

    lastSpeakTime = new Date()
    isSpeaking = true
    speakingText = text
    document.getElementById('stopSpeaking').disabled = false
    avatarSynthesizer.speakSsmlAsync(ssml).then(
        (result) => {
            if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
                console.log(`Speech synthesized to speaker for text [ ${text} ]. Result ID: ${result.resultId}`)
                lastSpeakTime = new Date()
            } else {
                console.log(`Error occurred while speaking the SSML. Result ID: ${result.resultId}`)
            }

            speakingText = ''

            if (spokenTextQueue.length > 0) {
                speakNext(spokenTextQueue.shift())
            } else {
                isSpeaking = false
                document.getElementById('stopSpeaking').disabled = true
            }
        }).catch(
            (error) => {
                console.log(`Error occurred while speaking the SSML: [ ${error} ]`)

                speakingText = ''

                if (spokenTextQueue.length > 0) {
                    speakNext(spokenTextQueue.shift())
                } else {
                    isSpeaking = false
                    document.getElementById('stopSpeaking').disabled = true
                }
            }
        )
}

function stopSpeaking() {
    lastInteractionTime = new Date()
    spokenTextQueue = []
    avatarSynthesizer.stopSpeakingAsync().then(
        () => {
            isSpeaking = false
            document.getElementById('stopSpeaking').disabled = true
            console.log("[" + (new Date()).toISOString() + "] Stop speaking request sent.")
        }
    ).catch(
        (error) => {
            console.log("Error occurred while stopping speaking: " + error)
        }
    )
}

function handleUserQuery(userQuery, userQueryHTML, imgUrlPath) {
    lastInteractionTime = new Date()
    let contentMessage = userQuery
    if (imgUrlPath.trim()) {
        contentMessage = [
            {
                "type": "text",
                "text": userQuery
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": imgUrlPath
                }
            }
        ]
    }
    let chatMessage = {
        role: 'user',
        content: contentMessage
    }

    messages.push(chatMessage)
    let chatHistoryTextArea = document.getElementById('chatHistory')

    if (chatHistoryTextArea.innerHTML !== '' && !chatHistoryTextArea.innerHTML.endsWith('\n\n')) {
        chatHistoryTextArea.innerHTML += '\n\n'
    }

    chatHistoryTextArea.innerHTML += imgUrlPath.trim() ? "<br/><br/>User: " + userQueryHTML : "<br/><br/>User: " + userQuery + "<br/>";

    chatHistoryTextArea.scrollTop = chatHistoryTextArea.scrollHeight

    // Stop previous speaking if there is any
    if (isSpeaking) {
        stopSpeaking()
    }

    // For 'bring your data' scenario, chat API currently has long (4s+) latency
    // We return some quick reply here before the chat API returns to mitigate.
    if (dataSources.length > 0 && enableQuickReply) {
        speak(getQuickReply(), 2000)
    }

    const azureOpenAIEndpoint = window.azureConfig?.openai_endpoint
    const azureOpenAIApiKey = window.azureConfig?.openai_key
    const azureOpenAIDeploymentName = document.getElementById('azureOpenAIDeploymentName').value

    let url = `${azureOpenAIEndpoint}/openai/deployments/${azureOpenAIDeploymentName}/chat/completions?api-version=2024-12-01-preview`
    let body = JSON.stringify({
        messages: messages,
        stream: true
    })

    // Debug logging
    console.log('OpenAI API Request:', {
        model: azureOpenAIDeploymentName,
        endpoint: azureOpenAIEndpoint,
        url: url,
        messageCount: messages.length
    })

    // No On Your Data support in simplified UI (dataSources is always empty)

    let assistantReply = ''
    let toolContent = ''
    let spokenSentence = ''
    let displaySentence = ''

    fetch(url, {
        method: 'POST',
        headers: {
            'api-key': azureOpenAIApiKey,
            'Content-Type': 'application/json'
        },
        body: body
    })
        .then(response => {
            if (!response.ok) {
                // Enhanced error handling for better debugging
                return response.text().then(errorText => {
                    console.error(`Chat API Error - Status: ${response.status}, Response: ${errorText}`)
                    
                    let errorMessage = `Chat API failed with status ${response.status}`
                    
                    try {
                        const errorJson = JSON.parse(errorText)
                        if (errorJson.error && errorJson.error.message) {
                            errorMessage = errorJson.error.message
                        }
                    } catch (e) {
                        // If not JSON, use the text response
                        if (errorText.length > 0 && errorText.length < 200) {
                            errorMessage += `: ${errorText}`
                        }
                    }
                    
                    // Show user-friendly error message
                    let chatHistoryTextArea = document.getElementById('chatHistory')
                    chatHistoryTextArea.innerHTML += `<br/><br/><span style="color: red; font-weight: bold;">Error:</span> ${errorMessage}<br/>`
                    chatHistoryTextArea.innerHTML += `<span style="color: #666; font-size: 12px;">Model: ${azureOpenAIDeploymentName} | Check Azure OpenAI deployment configuration</span><br/>`
                    chatHistoryTextArea.scrollTop = chatHistoryTextArea.scrollHeight
                    
                    throw new Error(errorMessage)
                })
            }

            let chatHistoryTextArea = document.getElementById('chatHistory')
            chatHistoryTextArea.innerHTML += imgUrlPath.trim() ? 'Assistant: ' : '<br/>Assistant: '

            const reader = response.body.getReader()

            // Function to recursively read chunks from the stream
            function read(previousChunkString = '') {
                return reader.read().then(({ value, done }) => {
                    // Check if there is still data to read
                    if (done) {
                        // Stream complete
                        return
                    }

                    // Process the chunk of data (value)
                    let chunkString = new TextDecoder().decode(value, { stream: true })
                    if (previousChunkString !== '') {
                        // Concatenate the previous chunk string in case it is incomplete
                        chunkString = previousChunkString + chunkString
                    }

                    if (!chunkString.endsWith('}\n\n') && !chunkString.endsWith('[DONE]\n\n')) {
                        // This is a incomplete chunk, read the next chunk
                        return read(chunkString)
                    }

                    chunkString.split('\n\n').forEach((line) => {
                        try {
                            if (line.startsWith('data:') && !line.endsWith('[DONE]')) {
                                const responseJson = JSON.parse(line.substring(5).trim())
                                let responseToken = undefined
                                if (dataSources.length === 0) {
                                    responseToken = responseJson.choices[0].delta.content
                                } else {
                                    let role = responseJson.choices[0].messages[0].delta.role
                                    if (role === 'tool') {
                                        toolContent = responseJson.choices[0].messages[0].delta.content
                                    } else {
                                        responseToken = responseJson.choices[0].messages[0].delta.content
                                        if (responseToken !== undefined) {
                                            if (byodDocRegex.test(responseToken)) {
                                                responseToken = responseToken.replace(byodDocRegex, '').trim()
                                            }

                                            if (responseToken === '[DONE]') {
                                                responseToken = undefined
                                            }
                                        }
                                    }
                                }

                                if (responseToken !== undefined && responseToken !== null) {
                                    assistantReply += responseToken // build up the assistant message
                                    displaySentence += responseToken // build up the display sentence

                                    if (responseToken === '\n' || responseToken === '\n\n') {
                                        spokenSentence += responseToken
                                        speak(spokenSentence)
                                        spokenSentence = ''
                                    } else {
                                        spokenSentence += responseToken // build up the spoken sentence

                                        responseToken = responseToken.replace(/\n/g, '')
                                        if (responseToken.length === 1 || responseToken.length === 2) {
                                            for (let i = 0; i < sentenceLevelPunctuations.length; ++i) {
                                                let sentenceLevelPunctuation = sentenceLevelPunctuations[i]
                                                if (responseToken.startsWith(sentenceLevelPunctuation)) {
                                                    speak(spokenSentence)
                                                    spokenSentence = ''
                                                    break
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        } catch (error) {
                            console.log(`Error occurred while parsing the response: ${error}`)
                            console.log(chunkString)
                        }
                    })

                    if (!enableDisplayTextAlignmentWithSpeech) {
                        chatHistoryTextArea.innerHTML += displaySentence.replace(/\n/g, '<br/>')
                        chatHistoryTextArea.scrollTop = chatHistoryTextArea.scrollHeight
                        displaySentence = ''
                    }

                    // Continue reading the next chunk
                    return read()
                })
            }

            // Start reading the stream
            return read()
        })
        .then(() => {
            if (spokenSentence !== '') {
                speak(spokenSentence)
                spokenSentence = ''
            }

            if (dataSources.length > 0) {
                let toolMessage = {
                    role: 'tool',
                    content: toolContent
                }

                messages.push(toolMessage)
            }

            let assistantMessage = {
                role: 'assistant',
                content: assistantReply
            }

            messages.push(assistantMessage)
        })
        .catch(error => {
            console.error('OpenAI API Error:', error)
            
            let chatHistoryTextArea = document.getElementById('chatHistory')
            chatHistoryTextArea.innerHTML += `<br/><br/><span style="color: red; font-weight: bold;">Connection Error:</span> ${error.message}<br/>`
            chatHistoryTextArea.innerHTML += `<span style="color: #666; font-size: 12px;">Please check your internet connection and Azure OpenAI configuration</span><br/>`
            chatHistoryTextArea.scrollTop = chatHistoryTextArea.scrollHeight
        })
}

function getQuickReply() {
    return quickReplies[Math.floor(Math.random() * quickReplies.length)]
}

function checkHung() {
    // Check whether the avatar video stream is hung, by checking whether the video time is advancing
    let videoElement = document.getElementById('videoPlayer')
    if (videoElement !== null && videoElement !== undefined && sessionActive) {
        let videoTime = videoElement.currentTime
        setTimeout(() => {
            // Check whether the video time is advancing
            if (videoElement.currentTime === videoTime) {
                // Check whether the session is active to avoid duplicatedly triggering reconnect
                if (sessionActive) {
                    sessionActive = false
                    if (document.getElementById('autoReconnectAvatar').checked) {
                        // No longer reconnect when there is no interaction for a while - extended to 30 minutes
                        if (new Date() - lastInteractionTime < 1800000) {
                            console.log(`[${(new Date()).toISOString()}] The video stream got disconnected, need reconnect.`)
                            isReconnecting = true
                            // Remove data channel onmessage callback to avoid duplicatedly triggering reconnect
                            peerConnectionDataChannel.onmessage = null
                            // Release the existing avatar connection
                            if (avatarSynthesizer !== undefined) {
                                avatarSynthesizer.close()
                            }

                            // Setup a new avatar connection
                            connectAvatar()
                        }
                    }
                }
            }
        }, 2000)
    }
}

function checkLastSpeak() {
    if (lastSpeakTime === undefined) {
        return
    }

    let currentTime = new Date()
    if (currentTime - lastSpeakTime > 15000) {
        if (document.getElementById('useLocalVideoForIdle').checked && sessionActive && !isSpeaking) {
            disconnectAvatar()
            document.getElementById('localVideo').hidden = false
            document.getElementById('remoteVideo').style.width = '0.1px'
            sessionActive = false
        }
    }
}

function handleAvatarConfigChange(configType) {
    console.log(`[${(new Date()).toISOString()}] Avatar ${configType} configuration changed`)
    
    // Only restart if session is currently active and not already reconnecting
    if (sessionActive && !isReconnecting && !userClosedSession) {
        console.log(`[${(new Date()).toISOString()}] Restarting avatar session due to ${configType} change...`)
        
        // Stop any current speaking
        if (isSpeaking) {
            stopSpeaking()
        }
        
        // Mark as reconnecting to prevent duplicate restarts
        isReconnecting = true
        
        // Disconnect current session
        disconnectAvatar()
        
        // Brief delay to ensure cleanup completes before reconnecting
        setTimeout(() => {
            console.log(`[${(new Date()).toISOString()}] Reconnecting with new ${configType} configuration...`)
            connectAvatar()
        }, 1000)
    }
}

window.onload = () => {
    setInterval(() => {
        checkHung()
        checkLastSpeak()
    }, 2000) // Check session activity every 2 seconds

    // Add event listeners for avatar configuration changes
    document.getElementById('talkingAvatarCharacter').addEventListener('change', () => {
        handleAvatarConfigChange('character')
    })
    
    document.getElementById('talkingAvatarStyle').addEventListener('change', () => {
        handleAvatarConfigChange('style')
    })
    
    document.getElementById('ttsVoice').addEventListener('change', () => {
        handleAvatarConfigChange('voice')
    })
}

window.startSession = () => {
    lastInteractionTime = new Date()
    userClosedSession = false  // Reset the flag before starting
    
    if (document.getElementById('useLocalVideoForIdle').checked) {
        document.getElementById('startSession').disabled = true
        document.getElementById('configuration').hidden = true
        document.getElementById('microphone').disabled = false
        document.getElementById('stopSession').disabled = false
        document.getElementById('localVideo').hidden = false
        document.getElementById('remoteVideo').style.width = '0.1px'
        document.getElementById('chatHistory').hidden = false
        document.getElementById('showTypeMessage').disabled = false
        return
    }

    connectAvatar()
}

window.stopSession = () => {
    lastInteractionTime = new Date()
    document.getElementById('startSession').disabled = false
    document.getElementById('microphone').disabled = true
    document.getElementById('stopSession').disabled = true
    document.getElementById('configuration').hidden = false
    document.getElementById('chatHistory').hidden = true
    document.getElementById('showTypeMessage').checked = false
    document.getElementById('showTypeMessage').disabled = true
    document.getElementById('userMessageBox').hidden = true
    document.getElementById('uploadImgIcon').hidden = true
    if (document.getElementById('useLocalVideoForIdle').checked) {
        document.getElementById('localVideo').hidden = true
    }

    userClosedSession = true
    disconnectAvatar()
}

window.clearChatHistory = () => {
    lastInteractionTime = new Date()
    document.getElementById('chatHistory').innerHTML = ''
    initMessages()
}

window.microphone = () => {
    lastInteractionTime = new Date()
    if (document.getElementById('microphone').innerHTML === 'Stop Microphone') {
        // Stop microphone
        document.getElementById('microphone').disabled = true
        speechRecognizer.stopContinuousRecognitionAsync(
            () => {
                document.getElementById('microphone').innerHTML = 'Start Microphone'
                document.getElementById('microphone').disabled = false
            },
            (err) => {
                console.log("Failed to stop continuous recognition:", err)
                document.getElementById('microphone').disabled = false
            })

        return
    }

    if (document.getElementById('useLocalVideoForIdle').checked) {
        if (!sessionActive) {
            connectAvatar()
        }

        setTimeout(() => {
            document.getElementById('audioPlayer').play()
        }, 5000)
    } else {
        document.getElementById('audioPlayer').play()
    }

    document.getElementById('microphone').disabled = true
    speechRecognizer.recognized = async (s, e) => {
        if (e.result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {
            let userQuery = e.result.text.trim()
            if (userQuery === '') {
                return
            }

            // Auto stop microphone when a phrase is recognized, when it's not continuous conversation mode
            if (!document.getElementById('continuousConversation').checked) {
                document.getElementById('microphone').disabled = true
                speechRecognizer.stopContinuousRecognitionAsync(
                    () => {
                        document.getElementById('microphone').innerHTML = 'Start Microphone'
                        document.getElementById('microphone').disabled = false
                    }, (err) => {
                        console.log("Failed to stop continuous recognition:", err)
                        document.getElementById('microphone').disabled = false
                    })
            }

            handleUserQuery(userQuery, "", "")
        }
    }

    speechRecognizer.startContinuousRecognitionAsync(
        () => {
            document.getElementById('microphone').innerHTML = 'Stop Microphone'
            document.getElementById('microphone').disabled = false
        }, (err) => {
            console.log("Failed to start continuous recognition:", err)
            document.getElementById('microphone').disabled = false
        })
}

window.updateTypeMessageBox = () => {
    if (document.getElementById('showTypeMessage').checked) {
        document.getElementById('userMessageBox').hidden = false
        document.getElementById('uploadImgIcon').hidden = false
        document.getElementById('userMessageBox').addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                const userQuery = document.getElementById('userMessageBox').innerText
                const messageBox = document.getElementById('userMessageBox')
                const childImg = messageBox.querySelector("#picInput")
                if (childImg) {
                    childImg.style.width = "200px"
                    childImg.style.height = "200px"
                }
                let userQueryHTML = messageBox.innerHTML.trim("")
                if (userQueryHTML.startsWith('<img')) {
                    userQueryHTML = "<br/>" + userQueryHTML
                }
                if (userQuery !== '') {
                    handleUserQuery(userQuery.trim(''), userQueryHTML, imgUrl)
                    document.getElementById('userMessageBox').innerHTML = ''
                    imgUrl = ""
                }
            }
        })
        document.getElementById('uploadImgIcon').addEventListener('click', function() {
            imgUrl = "https://wallpaperaccess.com/full/528436.jpg"
            const userMessage = document.getElementById("userMessageBox");
            const childImg = userMessage.querySelector("#picInput");
            if (childImg) {
                userMessage.removeChild(childImg)
            }
            userMessage.innerHTML += '<br/><img id="picInput" src="https://wallpaperaccess.com/full/528436.jpg" style="width:100px;height:100px"/><br/><br/>'
        });
    } else {
        document.getElementById('userMessageBox').hidden = true
        document.getElementById('uploadImgIcon').hidden = true
        imgUrl = ""
    }
}

window.updateLocalVideoForIdle = () => {
    if (document.getElementById('useLocalVideoForIdle').checked) {
        document.getElementById('showTypeMessageCheckbox').hidden = true
    } else {
        document.getElementById('showTypeMessageCheckbox').hidden = false
    }
}
