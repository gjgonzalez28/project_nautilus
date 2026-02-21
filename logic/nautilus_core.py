import json
import os

class NautilusCore:
    def __init__(self):
        # Dynamically find the path so it doesn't break if you move folders
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(base_dir, 'data', 'machine_library.json')
        self.db = self._load_db()

    def _load_db(self):
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def clean_text(self, text):
        return "".join(text.split()).replace("_", "").upper()

    def get_info(self, search_id):
        """Retrieve machine or era entry by ID."""
        clean_search = self.clean_text(search_id)
        for item in self.db:
            if self.clean_text(item['id']) == clean_search:
                return item
        return None

    def get_symptoms_by_era(self, era):
        """Retrieve all symptom entries for a specific era (EM, Solid State, Digital, etc.)."""
        results = []
        for item in self.db:
            if item.get('era', '').lower() == era.lower():
                if 'symptoms' in item:
                    results.append({
                        'machine_id': item['id'],
                        'name': item.get('name', 'Unknown'),
                        'era': item.get('era', era),
                        'manufacturer': item.get('manufacturer', 'Unknown'),
                        'symptoms': item['symptoms']
                    })
        return results

    def get_symptoms_by_machine(self, machine_id):
        """Retrieve all symptoms for a specific machine ID."""
        machine = self.get_info(machine_id)
        if machine and 'symptoms' in machine:
            return machine['symptoms']
        return []

    def search_symptom_by_keyword(self, keyword):
        """Search all machines for symptom matching keyword (case-insensitive)."""
        results = []
        keyword_clean = keyword.lower()
        for item in self.db:
            if 'symptoms' in item:
                for symptom in item['symptoms']:
                    symptom_text = symptom.get('symptom', '').lower()
                    if keyword_clean in symptom_text:
                        results.append({
                            'machine_id': item['id'],
                            'machine_name': item.get('name', 'Unknown'),
                            'era': item.get('era', 'Unknown'),
                            'symptom': symptom
                        })
        return results

    def get_led_flash_codes(self):
        """Retrieve all LED flash code entries (for Bally MPU diagnostics)."""
        results = []
        for item in self.db:
            if item.get('id') == 'BALLY_1978_MPU' and 'symptoms' in item:
                for symptom in item['symptoms']:
                    if 'led_code' in symptom:
                        results.append(symptom)
        return results

    def get_all_eras(self):
        """Get list of all available eras in database."""
        eras = set()
        for item in self.db:
            if 'era' in item:
                eras.add(item['era'])
        return sorted(list(eras))