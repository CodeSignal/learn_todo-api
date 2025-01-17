from flask import Blueprint, request
from services.note_service import NoteService

notes_bp = Blueprint("notes", __name__)

@notes_bp.route("", methods=["POST"])
def upload_note():
    """Upload a new note in .txt format"""
    return NoteService.upload_note(request)

@notes_bp.route("/<note_name>", methods=["GET"])
def download_note(note_name):
    """Download an existing note by its name"""
    return NoteService.download_note(note_name)

@notes_bp.route("/<note_name>", methods=["DELETE"])
def delete_note(note_name):
    """Delete an existing note by its name"""
    return NoteService.delete_note(note_name) 