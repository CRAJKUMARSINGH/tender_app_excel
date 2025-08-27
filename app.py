import os
import pandas as pd
import xlsxwriter
import logging
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import hashlib
from functools import lru_cache
import threading
import time
from collections import defaultdict
import traceback
from bidder_manager import bidder_manager

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Analytics and monitoring
class Analytics:
    def __init__(self):
        self.stats_file = 'analytics.json'
        self.stats = self.load_stats()
    
    def load_stats(self):
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")
        return {
            'total_uploads': 0,
            'successful_generations': 0,
            'errors': 0,
            'file_types': defaultdict(int),
            'processing_times': [],
            'last_activity': None
        }
    
    def save_stats(self):
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
    
    def record_upload(self, filename, file_type, success=True, processing_time=None):
        self.stats['total_uploads'] += 1
        self.stats['file_types'][file_type] += 1
        self.stats['last_activity'] = datetime.now().isoformat()
        
        if success:
            self.stats['successful_generations'] += 1
        else:
            self.stats['errors'] += 1
        
        if processing_time:
            self.stats['processing_times'].append(processing_time)
            # Keep only last 100 processing times
            if len(self.stats['processing_times']) > 100:
                self.stats['processing_times'] = self.stats['processing_times'][-100:]
        
        self.save_stats()

# Global analytics instance
analytics = Analytics()

# Progress tracking
class ProgressTracker:
    def __init__(self):
        self.progress = {}
        self.lock = threading.Lock()
    
    def start_task(self, task_id, total_steps):
        with self.lock:
            self.progress[task_id] = {
                'current': 0,
                'total': total_steps,
                'status': 'running',
                'start_time': time.time(),
                'messages': []
            }
    
    def update_progress(self, task_id, step, message=""):
        with self.lock:
            if task_id in self.progress:
                self.progress[task_id]['current'] = step
                if message:
                    self.progress[task_id]['messages'].append(message)
    
    def complete_task(self, task_id, success=True):
        with self.lock:
            if task_id in self.progress:
                self.progress[task_id]['status'] = 'completed' if success else 'failed'
                self.progress[task_id]['end_time'] = time.time()
    
    def get_progress(self, task_id):
        with self.lock:
            return self.progress.get(task_id, {})

# Global progress tracker
progress_tracker = ProgressTracker()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Validate file size with enhanced error handling"""
    try:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        return size <= MAX_FILE_SIZE
    except Exception as e:
        logger.error(f"Error validating file size: {e}")
        return False

def validate_percentile(value):
    """Enhanced percentile validation with better error messages"""
    try:
        if value is None or value == '':
            return False, "Percentile value cannot be empty"
        
        # Convert to float
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False, "Percentile must be a valid number"
        
        # Check range
        if float_value < -99.99 or float_value > 99.99:
            return False, f"Percentile must be between -99.99% and +99.99% (got {float_value}%)"
        
        return True, "Valid percentile"
    except Exception as e:
        logger.error(f"Error in percentile validation: {e}")
        return False, f"Validation error: {str(e)}"

@lru_cache(maxsize=20)  # Increased cache size
def parse_input_file_cached(file_path):
    """Cached version of parse_input_file for better performance"""
    return parse_input_file(file_path)

def parse_input_file(file_path):
    """Enhanced parse input Excel file with better error handling and validation"""
    start_time = time.time()
    task_id = f"parse_{hashlib.md5(file_path.encode()).hexdigest()[:8]}"
    
    try:
        progress_tracker.start_task(task_id, 5)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        progress_tracker.update_progress(task_id, 1, "File found, checking size...")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
        
        progress_tracker.update_progress(task_id, 2, "Reading Excel file...")
        
        # Read Excel file with enhanced error handling
        try:
            df = pd.read_excel(file_path, header=None, engine='openpyxl')
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {str(e)}")
        
        progress_tracker.update_progress(task_id, 3, "Extracting NIT information...")
        
        # Extract NIT information with better parsing
        nit_info = {}
        works_data = []
        
        # Enhanced NIT extraction
        for index, row in df.iterrows():
            row_str = ' '.join(str(cell) for cell in row if pd.notna(cell))
            if 'NIT' in row_str.upper() and 'NUMBER' in row_str.upper():
                # Look for NIT number in the same row or next row
                for cell in row:
                    if pd.notna(cell) and isinstance(cell, str) and any(char.isdigit() for char in cell):
                        nit_info['nit_number'] = str(cell).strip()
                        break
                if not nit_info.get('nit_number'):
                    # Check next row
                    if index + 1 < len(df):
                        for cell in df.iloc[index + 1]:
                            if pd.notna(cell) and isinstance(cell, str) and any(char.isdigit() for char in cell):
                                nit_info['nit_number'] = str(cell).strip()
                                break
                break
        
        progress_tracker.update_progress(task_id, 4, "Extracting works data...")
        
        # Enhanced works extraction
        for index, row in df.iterrows():
            row_str = ' '.join(str(cell) for cell in row if pd.notna(cell))
            if 'WORK' in row_str.upper() and any(char.isdigit() for char in row_str):
                work_name = None
                for cell in row:
                    if pd.notna(cell) and isinstance(cell, str) and 'WORK' in cell.upper():
                        work_name = str(cell).strip()
                        break
                
                if work_name:
                    works_data.append({
                        'name': work_name,
                        'row_index': index
                    })
        
        progress_tracker.update_progress(task_id, 5, "Validation complete...")
        
        if not works_data:
            raise ValueError("No works data found in the file")
        
        processing_time = time.time() - start_time
        progress_tracker.complete_task(task_id, True)
        
        logger.info(f"File parsed successfully in {processing_time:.2f}s")
        
        return {
            'nit_info': nit_info,
            'works': works_data,
            'filename': os.path.basename(file_path),
            'processing_time': processing_time
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        progress_tracker.complete_task(task_id, False)
        logger.error(f"Error parsing file: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Failed to parse input file: {str(e)}")

def create_excel_template(data, template_type, output_path):
    """Enhanced Excel template creation with better formatting and error handling"""
    try:
        workbook = xlsxwriter.Workbook(output_path)
        
        # Enhanced formats with better styling
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'font_size': 12
        })
        
        cell_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'font_size': 11
        })
        
        number_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '0.00',
            'font_size': 11
        })
        
        worksheet = workbook.add_worksheet()
        
        # Set page properties based on template type
        if template_type == 'comparison':
            worksheet.set_landscape()
            worksheet.set_paper(9)  # A4
            worksheet.fit_to_pages(1, 0)  # Fit to 1 page wide
        else:
            worksheet.set_portrait()
            worksheet.set_paper(9)  # A4
            worksheet.fit_to_pages(1, 1)  # Fit to 1 page
        
        # Write title
        title = f"{template_type.upper()} TEMPLATE"
        worksheet.merge_range('A1:D1', title, header_format)
        
        # Write NIT information
        row = 2
        worksheet.write(row, 0, 'NIT Number:', header_format)
        worksheet.write(row, 1, data['nit_info'].get('nit_number', 'N/A'), cell_format)
        
        # Write works data
        row += 2
        worksheet.write(row, 0, 'Work Name', header_format)
        worksheet.write(row, 1, 'Number of Bidders', header_format)
        worksheet.write(row, 2, 'Bidder Percentiles', header_format)
        worksheet.write(row, 3, 'Remarks', header_format)
        
        row += 1
        for work in data['works']:
            worksheet.write(row, 0, work['name'], cell_format)
            worksheet.write(row, 1, '', number_format)  # Empty for user input
            worksheet.write(row, 2, '', cell_format)    # Empty for user input
            worksheet.write(row, 3, '', cell_format)    # Empty for user input
            row += 1
        
        # Add box image for comparison sheet with enhanced positioning
        if template_type == 'comparison':
            try:
                box_image_path = 'Attached_assets/box.png'
                if os.path.exists(box_image_path):
                    image_row = row + 2
                    worksheet.insert_image(image_row, 0, box_image_path, {
                        'x_offset': 10,
                        'y_offset': 10,
                        'x_scale': 0.8,
                        'y_scale': 0.8,
                        'positioning': 1  # Move and size with cells
                    })
                    logger.info(f"Box image added to comparison sheet at row {image_row}")
                else:
                    logger.warning(f"Box image not found at {box_image_path}")
            except Exception as e:
                logger.error(f"Error adding box image: {str(e)}")
        
        # Set column widths for better readability
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 30)
        
        workbook.close()
        logger.info(f"Template {template_type} created successfully: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating template {template_type}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def generate_all_templates(data, output_dir):
    """Enhanced template generation with progress tracking"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        templates = ['comparison', 'scrutiny', 'evaluation', 'award']
        generated_files = []
        
        for i, template_type in enumerate(templates):
            output_path = os.path.join(output_dir, f"{template_type}_template.xlsx")
            create_excel_template(data, template_type, output_path)
            generated_files.append(output_path)
        
        return generated_files
        
    except Exception as e:
        logger.error(f"Error generating templates: {str(e)}")
        raise

@app.route('/')
def index():
    """Enhanced index route with analytics and bidder data"""
    try:
        # Get basic analytics for display
        stats = analytics.stats
        
        # Get bidder data for the interface
        recent_bidders = bidder_manager.get_recent_bidders(7)  # Last 7 days
        popular_bidders = bidder_manager.get_popular_bidders(10)
        bidder_stats = bidder_manager.get_bidder_stats()
        
        return render_template('index.html', 
                             stats=stats, 
                             recent_bidders=recent_bidders,
                             popular_bidders=popular_bidders,
                             bidder_stats=bidder_stats)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html', stats={})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Enhanced upload route with progress tracking and analytics"""
    start_time = time.time()
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload Excel files only (.xlsx, .xls)'}), 400
        
        if not validate_file_size(file):
            return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Parse file
        data = parse_input_file(file_path)
        
        # Record analytics
        processing_time = time.time() - start_time
        analytics.record_upload(filename, filename.split('.')[-1], True, processing_time)
        
        return jsonify({
            'success': True,
            'data': data,
            'processing_time': processing_time
        })
        
    except Exception as e:
        processing_time = time.time() - start_time
        analytics.record_upload(file.filename if 'file' in request.files else 'unknown', 'unknown', False, processing_time)
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_templates():
    """Enhanced template generation route with progress tracking"""
    try:
        data = request.json.get('data')
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Enhanced validation with detailed error messages
        for work_index, work in enumerate(data.get('works', [])):
            bidders = work.get('bidders', [])
            if not bidders:
                return jsonify({'error': f"No bidders found for {work['name']}"}), 400
            
            for bidder_index, bidder in enumerate(bidders):
                percentile = bidder.get('percentile')
                name = bidder.get('name', f'Bidder {bidder_index + 1}')
                
                # Check if percentile exists
                if percentile is None:
                    return jsonify({'error': f"Missing percentile for {work['name']} - {name}"}), 400
                
                # Validate percentile
                is_valid, message = validate_percentile(percentile)
                if not is_valid:
                    return jsonify({'error': f"Invalid percentile for {work['name']} - {name}: {message}"}), 400
                
                # Update bidder usage in database
                bidder_manager.update_bidder_usage(name, bidder.get('address', ''))
        
        # Generate templates
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(OUTPUT_FOLDER, f"templates_{timestamp}")
        
        generated_files = generate_all_templates(data, output_dir)
        
        # Create zip file for download
        import zipfile
        zip_path = os.path.join(OUTPUT_FOLDER, f"templates_{timestamp}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in generated_files:
                zipf.write(file_path, os.path.basename(file_path))
        
        # Record successful generation
        analytics.record_upload('template_generation', 'success', True)
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{os.path.basename(zip_path)}',
            'files': [os.path.basename(f) for f in generated_files],
            'zip_file': os.path.basename(zip_path)
        })
        
    except Exception as e:
        analytics.record_upload('template_generation', 'error', False)
        logger.error(f"Template generation error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Enhanced download route with security checks"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Security check - only allow downloading from OUTPUT_FOLDER
        if not os.path.abspath(file_path).startswith(os.path.abspath(OUTPUT_FOLDER)):
            return jsonify({'error': 'Access denied'}), 403
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<task_id>')
def get_progress(task_id):
    """Get progress for a specific task"""
    try:
        progress = progress_tracker.get_progress(task_id)
        return jsonify(progress)
    except Exception as e:
        logger.error(f"Progress error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics')
def get_analytics():
    """Get application analytics"""
    try:
        return jsonify(analytics.stats)
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bidders/search')
def search_bidders():
    """Search bidders by name or address"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'bidders': []})
        
        results = bidder_manager.search_bidders(query, limit)
        return jsonify({'bidders': results})
        
    except Exception as e:
        logger.error(f"Bidder search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bidders/recent')
def get_recent_bidders():
    """Get recently used bidders"""
    try:
        days = int(request.args.get('days', 30))
        bidders = bidder_manager.get_recent_bidders(days)
        return jsonify({'bidders': bidders})
        
    except Exception as e:
        logger.error(f"Recent bidders error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bidders/popular')
def get_popular_bidders():
    """Get popular bidders"""
    try:
        limit = int(request.args.get('limit', 10))
        bidders = bidder_manager.get_popular_bidders(limit)
        return jsonify({'bidders': bidders})
        
    except Exception as e:
        logger.error(f"Popular bidders error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bidders/suggestions')
def get_bidder_suggestions():
    """Get bidder name suggestions for autocomplete"""
    try:
        partial_name = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 5))
        
        suggestions = bidder_manager.get_bidder_suggestions(partial_name, limit)
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        logger.error(f"Bidder suggestions error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bidders/stats')
def get_bidder_stats():
    """Get bidder database statistics"""
    try:
        stats = bidder_manager.get_bidder_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Bidder stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bidders/all')
def get_all_bidders():
    """Get all bidders"""
    try:
        bidders = bidder_manager.get_all_bidders()
        return jsonify({'bidders': bidders})
        
    except Exception as e:
        logger.error(f"All bidders error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
