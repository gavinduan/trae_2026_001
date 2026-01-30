/**
 * Chinese New Year Customs QA Chat Client
 * 负责处理WebSocket连接、消息发送和UI更新
 */

class ChatClient {
    constructor() {
        // DOM元素
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.connectionStatus = document.getElementById('connection-status');
        this.sessionIdDisplay = document.getElementById('session-id');
        this.clearHistoryBtn = document.getElementById('clear-history');

        // 状态
        this.sessionId = this.getSessionId() || this.createSessionId();
        this.isConnected = false;
        this.isTyping = false;
        this.socket = null;

        // 初始化
        this.init();
    }

    init() {
        // 显示会话ID
        this.sessionIdDisplay.textContent = this.sessionId.substring(0, 8) + '...';

        // 绑定事件
        this.bindEvents();

        // 保持输入框焦点
        this.keepInputFocus();

        // 连接WebSocket
        this.connect();

        // 初始化快捷入口
        this.initQuickTopics();
    }

    bindEvents() {
        // 发送按钮点击
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // 输入框Enter键
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 自动调整输入框高度
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });

        // 清除历史按钮
        this.clearHistoryBtn.addEventListener('click', () => this.clearHistory());

        // 窗口关闭前提示
        window.addEventListener('beforeunload', () => {
            if (this.socket) {
                this.socket.disconnect();
            }
        });
    }

    connect() {
        // 创建WebSocket连接
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}`;

        this.socket = io(wsUrl, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });

        // 连接事件
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });

        // 消息事件
        this.socket.on('connected', (data) => {
            console.log('Server connected:', data);
            this.addSystemMessage('已连接到年俗问答服务器 🎊');
        });

        this.socket.on('bot_message', (data) => {
            this.hideTypingIndicator();
            this.addBotMessage(data.response, data.timestamp);
            this.setInputEnabled(true);
            this.focusInput();
        });

        this.socket.on('bot_stream_chunk', (data) => {
            if (data.is_complete) {
                this.hideTypingIndicator();
                this.finalizeStreamingMessage();
                this.setInputEnabled(true);
                this.focusInput();
            } else {
                this.updateStreamingMessage(data.chunk);
            }
        });

        this.socket.on('typing', (data) => {
            this.showTypingIndicator();
        });

        this.socket.on('error', (data) => {
            this.hideTypingIndicator();
            this.addErrorMessage(data.error || '发生错误，请重试');
            this.setInputEnabled(true);
            this.focusInput();
        });

        this.socket.on('history_cleared', (data) => {
            this.clearChatMessages();
            this.addSystemMessage('对话历史已清除');
        });
    }

    keepInputFocus() {
        // 点击聊天区域任意位置时保持输入框焦点
        document.addEventListener('click', (e) => {
            // 排除输入框自身的点击
            if (e.target !== this.messageInput) {
                // 延迟聚焦，确保点击事件处理完成
                setTimeout(() => this.focusInput(), 10);
            }
        });

        // 点击快捷话题按钮后也保持焦点
        document.querySelectorAll('.topic-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                setTimeout(() => this.focusInput(), 50);
            });
        });

        // 清除历史按钮点击后保持焦点
        this.clearHistoryBtn.addEventListener('click', () => {
            setTimeout(() => this.focusInput(), 50);
        });
    }

    focusInput() {
        if (this.messageInput && !this.messageInput.disabled) {
            this.messageInput.focus();
        }
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) {
            return;
        }

        if (!this.isConnected) {
            this.addErrorMessage('未连接到服务器，请检查网络连接');
            return;
        }

        // 显示用户消息
        this.addUserMessage(message);

        // 清空输入框
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        // 禁用输入
        this.setInputEnabled(false);

        // 显示加载指示器
        this.showTypingIndicator();

        // 发送消息到服务器
        this.socket.emit('user_message', {
            session_id: this.sessionId,
            message: message
        });

        // 发送后恢复焦点（用于流式响应完成后自动恢复）
        setTimeout(() => this.focusInput(), 100);
    }

    addUserMessage(message, timestamp = null) {
        const messageEl = this.createMessageElement(message, 'user', timestamp);
        this.chatMessages.appendChild(messageEl);
        this.scrollToBottom();
    }

    addBotMessage(message, timestamp = null) {
        const messageEl = this.createMessageElement(message, 'bot', timestamp);
        this.chatMessages.appendChild(messageEl);
        this.scrollToBottom();
    }

    addSystemMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'system-message';
        messageEl.innerHTML = `<p style="text-align: center; color: #999; font-size: 0.85rem; padding: 10px;">${message}</p>`;
        this.chatMessages.appendChild(messageEl);
        this.scrollToBottom();
    }

    addErrorMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'error-message';
        messageEl.textContent = message;
        this.chatMessages.appendChild(messageEl);
        this.scrollToBottom();
    }

    createMessageElement(message, type, timestamp = null) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = type === 'user' 
            ? '<i class="fas fa-user"></i>'
            : '<i class="fas fa-robot"></i>';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        // Render markdown for bot messages
        if (type === 'bot') {
            bubble.innerHTML = marked.parse(message);
        } else {
            bubble.textContent = message;
        }

        const time = document.createElement('div');
        time.className = 'timestamp';
        time.textContent = timestamp 
            ? new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
            : new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

        messageEl.appendChild(avatar);
        messageEl.appendChild(bubble);
        bubble.appendChild(time);

        return messageEl;
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.chatMessages.appendChild(this.typingIndicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    setInputEnabled(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
        this.messageInput.placeholder = enabled ? '输入你的问题...' : '正在思考...';
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.connectionStatus.className = 'status connected';
            this.connectionStatus.innerHTML = '<i class="fas fa-circle"></i> 已连接';
        } else {
            this.connectionStatus.className = 'status disconnected';
            this.connectionStatus.innerHTML = '<i class="fas fa-circle"></i> 未连接';
        }
    }

    clearChatMessages() {
        // 保留欢迎消息，移除其他消息
        const welcomeMsg = this.chatMessages.querySelector('.welcome-message');
        this.chatMessages.innerHTML = '';
        if (welcomeMsg) {
            this.chatMessages.appendChild(welcomeMsg);
        }
    }

    clearHistory() {
        if (confirm('确定要清除对话历史吗？')) {
            this.socket.emit('clear_history', { session_id: this.sessionId });
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateStreamingMessage(chunk) {
        let streamingMsg = this.chatMessages.querySelector('.message.streaming');
        
        if (!streamingMsg) {
            streamingMsg = document.createElement('div');
            streamingMsg.className = 'message bot streaming';
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
            
            const bubble = document.createElement('div');
            bubble.className = 'bubble streaming-bubble';
            bubble.textContent = '';
            
            streamingMsg.appendChild(avatar);
            streamingMsg.appendChild(bubble);
            this.chatMessages.appendChild(streamingMsg);
        }
        
        const streamingBubble = streamingMsg.querySelector('.streaming-bubble');
        if (streamingBubble) {
            streamingBubble.textContent += chunk;
        }
        
        this.scrollToBottom();
    }

    finalizeStreamingMessage() {
        const streamingMsg = this.chatMessages.querySelector('.message.streaming');
        if (streamingMsg) {
            streamingMsg.classList.remove('streaming');
            const streamingBubble = streamingMsg.querySelector('.streaming-bubble');
            if (streamingBubble) {
                streamingBubble.classList.remove('streaming-bubble');
                
                // Render markdown for the final message
                const content = streamingBubble.textContent;
                streamingBubble.innerHTML = marked.parse(content);
                
                const time = document.createElement('div');
                time.className = 'timestamp';
                time.textContent = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
                streamingBubble.appendChild(time);
            }
        }
    }

    initQuickTopics() {
        const topicBtns = document.querySelectorAll('.topic-btn');
        topicBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.dataset.message;
                this.messageInput.value = message;
                this.sendMessage();
            });
        });
    }

    getSessionId() {
        return localStorage.getItem('chat_session_id');
    }

    createSessionId() {
        const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chat_session_id', sessionId);
        return sessionId;
    }
}

// 初始化聊天客户端
document.addEventListener('DOMContentLoaded', () => {
    window.chatClient = new ChatClient();
});
