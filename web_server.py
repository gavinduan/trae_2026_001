#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web Chat Backend Server
Provides Flask + WebSocket server for the Chinese New Year customs QA system.
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.exceptions import HTTPException

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rag_controller import RAGController

class ChatServer:
    """Chat server for Chinese New Year customs QA system."""

    def __init__(self):
        """Initialize the chat server."""
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Initialize RAG controller
        knowledge_base_path = os.path.join(os.path.dirname(__file__), 'openspec', 'knowledge-base.json')
        self.rag_controller = RAGController(knowledge_base_path)

        # Session storage (use Redis in production)
        self.sessions: Dict[str, List[Dict]] = {}

        # Register routes
        self._register_routes()
        self._register_socket_events()

    def _register_routes(self):
        """Register Flask routes."""

        @self.app.route('/')
        def index():
            """Serve the main chat page."""
            return send_from_directory(os.path.join(os.path.dirname(__file__), 'web'), 'index.html')

        @self.app.route('/css/<path:filename>')
        def serve_css(filename):
            """Serve CSS files."""
            return send_from_directory(os.path.join(os.path.dirname(__file__), 'web', 'css'), filename)

        @self.app.route('/js/<path:filename>')
        def serve_js(filename):
            """Serve JavaScript files."""
            return send_from_directory(os.path.join(os.path.dirname(__file__), 'web', 'js'), filename)

        @self.app.route('/assets/<path:filename>')
        def serve_assets(filename):
            """Serve asset files."""
            return send_from_directory(os.path.join(os.path.dirname(__file__), 'web', 'assets'), filename)

        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'service': 'chinese-new-year-customs-qa',
                'llm_enabled': self.rag_controller.llm_enabled
            })

        @self.app.route('/api/chat', methods=['POST'])
        def chat_http():
            """HTTP endpoint for chat (WebSocket alternative)."""
            try:
                data = request.get_json()
                if not data or 'message' not in data:
                    return jsonify({'error': 'Missing message'}), 400

                session_id = data.get('session_id', str(uuid.uuid4()))
                message = data['message']
                context = self.sessions.get(session_id, [])

                # Process message
                response = self.rag_controller.process_query(message)

                # Store conversation
                if session_id not in self.sessions:
                    self.sessions[session_id] = []
                self.sessions[session_id].append({'role': 'user', 'content': message})
                self.sessions[session_id].append({'role': 'system', 'content': response})

                return jsonify({
                    'response': response,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/history/<session_id>', methods=['GET'])
        def get_history(session_id: str):
            """Get conversation history for a session."""
            history = self.sessions.get(session_id, [])
            return jsonify({'history': history, 'session_id': session_id})

        @self.app.route('/api/sessions', methods=['GET'])
        def list_sessions():
            """List all active sessions."""
            return jsonify({
                'sessions': list(self.sessions.keys()),
                'count': len(self.sessions)
            })

        @self.app.errorhandler(HTTPException)
        def handle_http_error(error):
            """Handle HTTP errors."""
            return jsonify({'error': error.description}), error.code

    def _register_socket_events(self):
        """Register SocketIO events."""

        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            emit('connected', {'status': 'connected', 'message': 'Welcome to Chinese New Year Customs QA!'})

        @self.socketio.on('user_message')
        def handle_user_message(data):
            """Handle user message via WebSocket."""
            try:
                session_id = data.get('session_id', str(uuid.uuid4()))
                message = data.get('message', '')

                if not message:
                    emit('error', {'error': 'Empty message'})
                    return

                # Store conversation
                if session_id not in self.sessions:
                    self.sessions[session_id] = []
                self.sessions[session_id].append({'role': 'user', 'content': message})

                # Process message
                response, source = self.rag_controller.process_query(message)

                # Check if response is from LLM
                if source == 'llm':
                    # Use streaming LLM response (thinking blocks already filtered in generator)
                    emit('typing', {'session_id': session_id}, broadcast=True)

                    full_response = ""
                    for chunk in self.rag_controller.llm_backend.generate_answer(message, self.sessions.get(session_id, []), stream=True):
                        full_response += chunk
                        emit('bot_stream_chunk', {
                            'chunk': chunk,
                            'session_id': session_id,
                            'is_complete': False
                        })

                    # Send completion signal
                    emit('bot_stream_chunk', {
                        'chunk': '',
                        'session_id': session_id,
                        'is_complete': True
                    })

                    self.sessions[session_id].append({'role': 'system', 'content': full_response})
                else:
                    # Use non-streaming response (knowledge base or fallback)
                    emit('bot_message', {
                        'response': response,
                        'session_id': session_id,
                        'timestamp': datetime.now().isoformat()
                    })

                    self.sessions[session_id].append({'role': 'system', 'content': response})

            except Exception as e:
                emit('error', {'error': str(e)})

        @self.socketio.on('typing')
        def handle_typing(data):
            """Handle typing indicator."""
            session_id = data.get('session_id', 'unknown')
            emit('typing', {'session_id': session_id}, broadcast=True)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            print('Client disconnected')

        @self.socketio.on('clear_history')
        def handle_clear_history(data):
            """Clear conversation history for a session."""
            session_id = data.get('session_id', '')
            if session_id and session_id in self.sessions:
                del self.sessions[session_id]
                emit('history_cleared', {'session_id': session_id})

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the chat server."""
        print(f"Starting Chinese New Year Customs QA Chat Server...")
        print(f"Server running at http://{host}:{port}")
        print(f"Web interface: http://{host}:{port}/")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def main():
    """Main entry point."""
    server = ChatServer()
    
    # Get configuration from environment or use defaults
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    server.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
