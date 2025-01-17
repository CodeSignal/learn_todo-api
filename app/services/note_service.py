import os
from flask import send_file, jsonify, current_app, make_response
from werkzeug.utils import secure_filename

class NoteService:
    NOTES_DIR = 'data/notes'  # Path relative to app directory
    MAX_NOTE_SIZE = 1024 * 1024  # 1MB max size for notes
    
    @classmethod
    def _get_notes_path(cls):
        """Get absolute path to notes directory"""
        return os.path.join(current_app.root_path, cls.NOTES_DIR)
    
    @classmethod
    def upload_note(cls, request):
        """Handle note upload"""
        if 'file' not in request.files:
            return jsonify({'error': 'No note file was provided'}), 400
            
        note_file = request.files['file']
        if note_file.filename == '':
            return jsonify({'error': 'No note file was selected'}), 400
            
        if not note_file.filename.endswith('.txt'):
            return jsonify({'error': 'Notes must be in .txt format'}), 400
        
        # Check file size
        note_file.seek(0, os.SEEK_END)
        size = note_file.tell()
        note_file.seek(0)
        
        if size > cls.MAX_NOTE_SIZE:
            return jsonify({'error': 'Note is too large. Maximum size is 1MB'}), 400
        
        # Validate content is text
        try:
            content = note_file.read().decode('utf-8')
            if not content.strip():
                return jsonify({'error': 'Note cannot be empty'}), 400
        except UnicodeDecodeError:
            return jsonify({'error': 'Note must contain valid text'}), 400
        finally:
            note_file.seek(0)
        
        note_name = secure_filename(note_file.filename)
        note_path = os.path.join(cls._get_notes_path(), note_name)
        note_file.save(note_path)
        
        return jsonify({
            'message': 'Note saved successfully',
            'note_name': note_name
        }), 201
    
    @classmethod
    def download_note(cls, note_name):
        """Handle note download"""
        note_path = os.path.join(cls._get_notes_path(), secure_filename(note_name))
            
        if not os.path.exists(note_path):
            return jsonify({'error': 'Note not found'}), 404
            
        try:
            return send_file(
                note_path,
                mimetype='text/plain',
                as_attachment=True,
                download_name=note_name
            )
        except Exception as e:
            return jsonify({'error': 'Failed to retrieve note'}), 500
            
    @classmethod
    def delete_note(cls, note_name):
        """Delete a note"""
        note_path = os.path.join(cls._get_notes_path(), secure_filename(note_name))
        
        if not os.path.exists(note_path):
            return jsonify({'error': 'Note not found'}), 404
            
        try:
            os.remove(note_path)
            return make_response('', 204)
        except Exception as e:
            return jsonify({'error': 'Failed to delete note'}), 500 