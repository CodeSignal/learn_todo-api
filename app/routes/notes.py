from flask import Blueprint, request
from services.note_service import NoteService

notes_bp = Blueprint("notes", __name__)

@notes_bp.route("", methods=["POST"])
def upload_note():
    """Upload a new note in .txt format
    ---
    tags:
      - notes
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Text file to upload. Must be .txt format, max size 1MB
    responses:
      201:
        description: Note created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message
            note_name:
              type: string
              description: Name of the uploaded note
      400:
        description: Invalid request - empty file or wrong format
    """
    return NoteService.upload_note(request)

@notes_bp.route("/<note_name>", methods=["GET"])
def download_note(note_name):
    """Download an existing note by its name
    ---
    tags:
      - notes
    parameters:
      - name: note_name
        in: path
        type: string
        required: true
        description: Name of the note to download
    responses:
      200:
        description: Note file content
        content:
          text/plain:
            schema:
              type: string
      404:
        description: Note not found
    """
    return NoteService.download_note(note_name)

@notes_bp.route("/<note_name>", methods=["DELETE"])
def delete_note(note_name):
    """Delete an existing note by its name
    ---
    tags:
      - notes
    parameters:
      - name: note_name
        in: path
        type: string
        required: true
        description: Name of the note to delete
    responses:
      204:
        description: Note deleted successfully
      404:
        description: Note not found
    """
    return NoteService.delete_note(note_name) 