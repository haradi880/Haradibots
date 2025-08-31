import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

class NotesManager:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.upload_folder = os.path.join(app.instance_path, 'notes_uploads')
        self.csv_file = os.path.join(app.instance_path, 'user_Notes.csv')
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Create CSV file if it doesn't exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'user_id', 'title', 'content', 'filename', 'created_at', 'updated_at'])
    
    def _read_notes(self):
        notes = []
        with open(self.csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                notes.append(row)
        return notes
    
    def _write_notes(self, notes):
        with open(self.csv_file, 'w', newline='') as f:
            fieldnames = ['id', 'user_id', 'title', 'content', 'filename', 'created_at', 'updated_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(notes)
    
    def _get_next_id(self):
        notes = self._read_notes()
        if not notes:
            return 1
        return max(int(note['id']) for note in notes) + 1
    
    def get_note_by_id(self, note_id, user_id):
        notes = self._read_notes()
        for note in notes:
            if note['id'] == str(note_id) and note['user_id'] == str(user_id):
                return note
        return None
    
    def get_user_notes(self, user_id, search_term=None):
        notes = self._read_notes()
        user_notes = [note for note in notes if note['user_id'] == str(user_id)]
        
        if search_term:
            search_term = search_term.lower()
            return [
                note for note in user_notes
                if (search_term in note['title'].lower() or 
                    search_term in note['content'].lower())
            ]
        return user_notes
    
    def create_note(self, user_id, title, content, file=None):
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(self.upload_folder, filename))
        
        notes = self._read_notes()
        new_note = {
            'id': str(self._get_next_id()),
            'user_id': str(user_id),
            'title': title,
            'content': content,
            'filename': filename,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        notes.append(new_note)
        self._write_notes(notes)
    
    def update_note(self, note_id, user_id, title, content, file=None, delete_file=False):
        notes = self._read_notes()
        note = self.get_note_by_id(note_id, user_id)
        if not note:
            return False
        
        filename = note['filename']
        
        if delete_file and filename:
            try:
                os.remove(os.path.join(self.upload_folder, filename))
            except OSError:
                pass
            filename = None
        
        if file and file.filename != '':
            # Remove old file if exists
            if filename:
                try:
                    os.remove(os.path.join(self.upload_folder, filename))
                except OSError:
                    pass
            # Save new file
            filename = secure_filename(file.filename)
            file.save(os.path.join(self.upload_folder, filename))
        
        # Update the note in the list
        for i, n in enumerate(notes):
            if n['id'] == str(note_id) and n['user_id'] == str(user_id):
                notes[i] = {
                    'id': str(note_id),
                    'user_id': str(user_id),
                    'title': title,
                    'content': content,
                    'filename': filename,
                    'created_at': note['created_at'],
                    'updated_at': datetime.now().isoformat()
                }
                break
        
        self._write_notes(notes)
        return True
    
    def delete_note(self, note_id, user_id):
        notes = self._read_notes()
        note = self.get_note_by_id(note_id, user_id)
        if not note:
            return False
        
        if note['filename']:
            try:
                os.remove(os.path.join(self.upload_folder, note['filename']))
            except OSError:
                pass
        
        # Remove the note from the list
        notes = [n for n in notes if not (n['id'] == str(note_id) and n['user_id'] == str(user_id))]
        
        self._write_notes(notes)
        return True
    
    def get_file_path(self, note_id, user_id):
        note = self.get_note_by_id(note_id, user_id)
        if not note or not note['filename']:
            return None
        return os.path.join(self.upload_folder, note['filename'])