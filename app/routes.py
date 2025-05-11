import os
from dotenv import load_dotenv
load_dotenv()
import json
import logging
import datetime
import re
import queue
from typing import Optional, Dict, Any, Tuple
import threading
import time
from flask import Blueprint, request, jsonify, render_template, send_from_directory, redirect, url_for
import sys
import requests

# Import optional dependencies - these will be checked at runtime
try:
    import sounddevice as sd
    import numpy as np
    from vosk import Model, KaldiRecognizer
    VOICE_RECOGNITION_AVAILABLE = True
except ImportError:
    VOICE_RECOGNITION_AVAILABLE = False

# Create a Blueprint instance
main = Blueprint('main', __name__)

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

# Import update_flag_safely
try:
    from update_flag import update_flag_safely
except Exception as e:
    print(f"Error importing update_flag: {e}")

# Try to import display manager for preview functionality
try:
    from display import get_display_manager
    DISPLAY_MODULE_AVAILABLE = True
except ImportError:
    DISPLAY_MODULE_AVAILABLE = False
    print("Display module not available for preview")

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@main.route('/preview')
def preview():
    """Display preview page for the e-paper display"""
    # Import config_manager to load the current configuration
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
    from config_manager import load_config
    
    config = load_config()
    display_image = None
    
    # Try to get the current display image from the mock display
    use_mock = False
    if DISPLAY_MODULE_AVAILABLE:
        display_manager = get_display_manager()
        if display_manager.is_mock_display():
            use_mock = True
            display_image = display_manager.get_mock_display_image()
    
    last_updated = config.get('current_flag', {}).get('timestamp', None)
    
    return render_template('preview.html', 
                          display_image=display_image, 
                          use_mock=use_mock,
                          last_updated=last_updated)

# --- Secure Token Helper ---
def _require_token():
    secret = os.environ.get('FLAG_SECRET') or 'your-secret-token'
    token = request.headers.get('X-Flag-Token')
    if not token or token != secret:
        return False
    return True

# --- Shared flag change logic ---
def _change_flag_internal(country):
    if not country:
        return jsonify({'status': 'error', 'message': 'Country not provided'}), 400
    try:
        success = update_flag_safely(country, force_cleanup=True)
        if success == 0:
            return jsonify({'status': 'success', 'message': f'Flag changed to {country}'}), 200
        else:
            return jsonify({
                'status': 'partial_success',
                'message': f'Flag metadata updated for {country}, but physical display may not have updated'
            }), 202
    except Exception as e:
        logging.error(f"Error changing flag: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- SECURE Endpoints under /secure/ ---
@main.route('/secure/change-flag', methods=['POST'])
def secure_change_flag():
    if not _require_token():
        return jsonify({'status': 'error', 'message': 'Forbidden: Invalid or missing token'}), 403
    # Check for country
    country = None
    if request.is_json:
        data = request.get_json()
        country = data.get('country')
    elif request.form:
        country = request.form.get('country')
    else:
        country = request.args.get('country')
    return _change_flag_internal(country)

@main.route('/secure/current-flag', methods=['GET'])
def secure_current_flag():
    if not _require_token():
        return jsonify({'status': 'error', 'message': 'Forbidden: Invalid or missing token'}), 403
    try:
        with open(os.path.join(os.path.dirname(__file__), 'static/data/flag.json'), 'r', encoding='utf-8') as f:
            flag_data = json.load(f)
        return jsonify(flag_data)
    except Exception as e:
        logging.error(f"Error reading flag.json: {e}")
        return jsonify({'status': 'error', 'message': 'Could not read current flag info.'}), 500

# OPEN endpoint for local use
@main.route('/current-flag', methods=['GET'])
def current_flag():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'static/data/flag.json'), 'r', encoding='utf-8') as f:
            flag_data = json.load(f)
        return jsonify(flag_data)
    except Exception as e:
        logging.error(f"Error reading flag.json: {e}")
        return jsonify({'status': 'error', 'message': 'Could not read current flag info.'}), 500

# OPEN endpoint for local use
@main.route('/change-flag', methods=['POST'])
def change_flag():
    # No authentication required
    country = None
    if request.is_json:
        data = request.get_json()
        country = data.get('country')
    elif request.form:
        country = request.form.get('country')
    else:
        country = request.args.get('country')
    return _change_flag_internal(country)

@main.route('/config', methods=['GET'])
def get_config():
    # Import config_manager here to avoid circular imports
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
    from config_manager import load_config
    
    # Load the configuration
    config = load_config()
    
    # Render the config template with the configuration data
    return render_template('config.html', config=config)

@main.route('/config', methods=['POST'])
def save_config():
    # Import config_manager here to avoid circular imports
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
    from config_manager import load_config, save_config
    
    # Load existing configuration
    config = load_config()
    
    # Update configuration from form data
    config['flag_display']['enabled'] = 'enabled' in request.form
    config['flag_display']['headless'] = 'headless' in request.form
    
    # Always use time-based scheduling
    config['flag_display']['use_fixed_times'] = True
    
    # Save time-based scheduling options
    config['flag_display']['time_interval'] = int(request.form.get('time_interval', 30))
    config['flag_display']['start_hour'] = int(request.form.get('start_hour', 0))
    config['flag_display']['start_minute'] = int(request.form.get('start_minute', 0))
    
    config['flag_display']['update_at_startup'] = 'update_at_startup' in request.form
    config['flag_display']['mode'] = request.form.get('display_mode', 'random')
    config['flag_display']['fixed_country'] = request.form.get('fixed_country', '')
    
    # Update display config
    config['display']['width'] = int(request.form.get('display_width', 800))
    config['display']['height'] = int(request.form.get('display_height', 480))
    
    # Save the configuration
    save_config(config)
    
    # Update display manager configuration if available
    if DISPLAY_MODULE_AVAILABLE:
        try:
            display_manager = get_display_manager(config.get('flag_display', {}))
            # The display manager will reinitialize with the new configuration
        except Exception as e:
            logging.error(f"Error updating display manager: {e}")
    
    # Reload the configuration to ensure it was saved correctly
    config = load_config()
    
    # Render the config template with the updated configuration data
    return render_template('config.html', config=config, message="Configuration saved successfully!", success=True)

@main.route('/update-flag', methods=['POST'])
def update_flag_now():
    # Import update_flag
    try:
        # Force cleanup the lock file if there were recent timeouts and use random country
        success = update_flag_safely(None, force_cleanup=True)
        
        # If request wants JSON response, return JSON
        if request.is_json or request.headers.get('Accept') == 'application/json':
            if success == 0:
                return jsonify({'status': 'success', 'message': 'Flag updated successfully!'}), 200
            else:
                return jsonify({
                    'status': 'partial_success', 
                    'message': 'Flag metadata updated, but physical display may not have updated.'
                }), 202
        
        # For normal form submissions, redirect to preview page if it exists
        referer = request.headers.get('Referer', '')
        if 'preview' in referer:
            return redirect(url_for('main.preview'))
        
        # Import config_manager to load the current configuration
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
        from config_manager import load_config
        config = load_config()
        
        if success == 0:
            return render_template('config.html', config=config, message="Flag updated successfully!", success=True)
        else:
            return render_template('config.html', config=config, 
                                  message="Flag metadata updated, but physical display may not have updated.", 
                                  success=True)
            
    except Exception as e:
        logging.error(f"Error updating flag: {str(e)}", exc_info=True)
        
        # If request wants JSON response, return JSON
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'status': 'error', 'message': str(e)}), 500
            
        # Import config_manager to load the current configuration
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
        from config_manager import load_config
        config = load_config()
        
        return render_template('config.html', config=config, 
                              message=f"Error updating flag: {str(e)}", 
                              success=False)

# --- Voice-based flag selection ---

def match_country(text: str) -> Optional[str]:
    """
    Attempts to match the transcribed text to a country name.
    
    Args:
        text: The transcribed text to match against country names
        
    Returns:
        The matched country name or None if no match found
    """
    if not text:
        return None
    
    # Load country data
    country_data_path = os.path.join(os.path.dirname(__file__), 'static/data/countries.json')
    try:
        with open(country_data_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
    except Exception as e:
        logging.error(f"Error loading countries data: {e}")
        return None
    
    # Clean and normalize the input text
    text = text.lower().strip()
    
    # Define keywords to identify country mentions
    trigger_phrases = [
        "change flag to", "change to", "switch to", "show me", 
        "display", "i want", "give me", "set flag to"
    ]
    
    # Remove trigger phrases from the text
    for phrase in trigger_phrases:
        text = text.replace(phrase, "").strip()
    
    # Try exact match first
    for country_name in countries.keys():
        if text == country_name.lower():
            return country_name
    
    # Try 'contains' match (with word boundaries to avoid partial matches)
    for country_name in countries.keys():
        # Create a pattern that matches the country name as a whole word
        pattern = r'\b' + re.escape(country_name.lower()) + r'\b'
        if re.search(pattern, text):
            return country_name
    
    # Handle common alternative names and potential voice recognition errors
    alt_names = {
        'usa': 'United States',
        'us': 'United States',
        'america': 'United States',
        'united states of america': 'United States',
        'uk': 'United Kingdom',
        'england': 'United Kingdom',
        'britain': 'United Kingdom',
        'great britain': 'United Kingdom',
        'uae': 'United Arab Emirates',
        'emirates': 'United Arab Emirates',
    }
    
    # Check if any alternative name is in the text
    for alt_name, country_name in alt_names.items():
        if alt_name in text:
            return country_name
    
    # If no match found, try to find partial matches
    best_match = None
    best_match_score = 0
    
    for country_name in countries.keys():
        # Calculate similarity - simple contains logic first
        if country_name.lower() in text:
            # Full country name is in the text
            return country_name
        
        # Count matching words as a simple metric
        country_words = set(country_name.lower().split())
        text_words = set(text.split())
        common_words = country_words.intersection(text_words)
        
        if len(common_words) > 0 and len(common_words) > best_match_score:
            best_match = country_name
            best_match_score = len(common_words)
    
    return best_match

# Removed TTS function since Home Assistant will handle this

# Helper function for audio processing in voice_listen
def _process_audio_for_speech(model, sample_rate, duration):
    """
    Process audio input to recognize speech and match country names.
    
    Args:
        model: The Vosk model for speech recognition
        sample_rate: The audio sample rate to use
        duration: How long to listen for (in seconds)
        
    Returns:
        tuple: (recognized_text, matched_country)
    """
    import sounddevice as sd
    import numpy as np
    from vosk import KaldiRecognizer
    from scipy.signal import resample_poly

    # Load country names from your existing JSON
    country_data_path = os.path.join(os.path.dirname(__file__), 'static/data/countries.json')
    with open(country_data_path, 'r', encoding='utf-8') as f:
        countries = list(json.load(f).keys())
    # Use lower-case words only and pass to the recognizer
    rec = KaldiRecognizer(model, 16000, json.dumps([c.lower() for c in countries]))
    rec.SetWords(True)
    rec.SetPartialWords(True)
    rec.SetMaxAlternatives(0)
    
    # Prepare for recording
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        if status:
            logging.warning(f"Audio callback status: {status}")
        gain_factor = 1.5  # Try 1.5 to 3.0 for boosting quiet input
        boosted = np.clip(indata.astype(np.float32) * gain_factor, -32767, 32767)
        max_val = np.max(np.abs(boosted))
        if max_val > 0:
            norm_indata = (boosted / max_val) * 32767
            norm_indata = norm_indata.astype(np.int16)
        else:
            norm_indata = boosted.astype(np.int16)
        logging.info(f"Callback indata shape: {indata.shape}, dtype: {indata.dtype}, mean abs: {abs(indata).mean()}, max abs: {max_val}")
        if any(norm_indata):
            q.put(norm_indata.copy())
    
    # Start recording
    logging.info("Starting voice recording...")
    
    recognized_text = None
    matched_country = None
    
    blocksize = 1024
    with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            device=1,  # Explicitly use USB mic (index 1)
            blocksize=blocksize,
            callback=callback
        ):
        logging.info(f"Listening for {duration} seconds on device 1 (USB mic) at {sample_rate}Hz, blocksize 1024...")
        timeout_start = time.time()
        partial_text = None
        while time.time() < timeout_start + duration:
            if not q.empty():
                data = q.get()
                logging.info(f"Original audio block shape: {data.shape}, dtype: {data.dtype}, mean abs: {np.mean(np.abs(data))}, max abs: {np.max(np.abs(data))}")
                # Resample if needed
                if sample_rate != 16000:
                    data_float = data.astype(np.float32)
                    resampled = resample_poly(data_float, 16000, int(sample_rate), axis=0)
                    logging.info(f"Resampled audio block shape: {resampled.shape}, dtype: {resampled.dtype}, mean abs: {np.mean(np.abs(resampled))}, max abs: {np.max(np.abs(resampled))}")
                    data = resampled.astype(np.int16)
                else:
                    logging.info("No resampling needed, using original audio block.")
                # Ensure audio is 1D before passing to Vosk
                if data.ndim > 1:
                    data = data.reshape(-1)
                    logging.info(f"Flattened audio block to shape: {data.shape}, dtype: {data.dtype}")
                # Vosk expects bytes
                data_bytes = data.tobytes()
                if rec.AcceptWaveform(data_bytes):
                    result = json.loads(rec.Result())
                    logging.info(f"Vosk interim result: {result}")
                    text = result.get('text', '')
                    if text:
                        logging.info(f"Recognized text: {text}")
                        recognized_text = text
                        country_name = match_country(text)
                        if country_name:
                            logging.info(f"Matched country: {country_name}")
                            matched_country = country_name
                            break
                # Fallback: check partials for possible matches
                partial = json.loads(rec.PartialResult())
                text = partial.get('partial', '')
                if text:
                    partial_text = text
                    logging.info(f"Vosk partial: {text}")
                    country_name = match_country(text)
                    if country_name:
                        recognized_text = text
                        matched_country = country_name
                        break
                else:
                    logging.info(f"Vosk partial result: {partial}")
        final_result = json.loads(rec.FinalResult())
        logging.info(f"Vosk final result: {final_result}")
        final_text = final_result.get('text', '')
        if final_text and not recognized_text:
            logging.info(f"Final recognized text: {final_text}")
            recognized_text = final_text
            country_name = match_country(final_text)
            if country_name:
                logging.info(f"Matched country from final text: {country_name}")
                matched_country = country_name
        # If still nothing, try last partial
        if not recognized_text and partial_text:
            recognized_text = partial_text
            country_name = match_country(partial_text)
            if country_name:
                matched_country = country_name
    return recognized_text, matched_country

# Helper function to find a supported sample rate
def _find_supported_sample_rate():
    """
    Find a supported audio sample rate for the current audio device.
    
    Returns:
        int: A supported sample rate
    """
    import sounddevice as sd
    # Get audio device info and supported sample rates
    try:
        device_info = sd.query_devices(kind='input')
        logging.info(f"Audio input device: {device_info['name']}")
        default_samplerate = int(device_info['default_samplerate'])
        logging.info(f"Default sample rate: {default_samplerate}")
    except Exception as e:
        logging.warning(f"Could not query audio devices: {str(e)}")
        default_samplerate = 44100  # Fallback to a common rate
    
    # Preferred sample rates - start with the known supported ones based on your device
    preferred_rates = [16000, 8000, 44100, 48000]
    blocksize = 1024
    
    # Target rate that we'll try to use
    sample_rate = None
    
    # First try the preferred rates for Vosk
    for rate in preferred_rates:
        try:
            logging.info(f"Testing sample rate: {rate} on device 1 (USB mic) with blocksize 1024")
            # Just test if we can open a stream with this rate
            # Using a context manager to ensure proper cleanup
            with sd.InputStream(samplerate=rate, channels=1, dtype='int16', device=1, blocksize=blocksize):
                # Successfully opened a stream with this rate
                logging.info(f"Successfully tested sample rate: {rate} on device 1 (USB mic)")
                sample_rate = rate
                break
        except Exception as e:
            logging.warning(f"Sample rate {rate} not supported: {str(e)}")
    
    # If none of the preferred rates work, use the default
    if sample_rate is None:
        logging.info(f"Using default sample rate: {default_samplerate}")
        sample_rate = default_samplerate
    
    logging.info(f"Using sample rate: {sample_rate}")
    return sample_rate

@main.route('/voice-listen', methods=['POST'])
def voice_listen():
    """
    Endpoint that listens for voice input, transcribes it, and tries to match
    the spoken text to a country name to change the flag.
    
    This endpoint is Home Assistant agnostic and only handles the voice recognition
    and flag changing functionality. The response can be used by Home Assistant
    or any other system to provide feedback to the user.
    """

    try:
        import sounddevice as sd
        from vosk import Model
        import numpy as np
        
        # Set up voice recognition
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/vosk-model-small-en-us-0.15')
        
        # Check if model exists
        if not os.path.exists(model_path):
            logging.error(f"Voice model not found at {model_path}")
            return jsonify({
                'status': 'error',
                'message': 'Voice recognition model not found. Please download and install it.'
            }), 500
        
        model = Model(model_path)
        
        # Find a supported sample rate
        sample_rate = _find_supported_sample_rate()
        logging.info(f"Using selected sample rate for voice recognition: {sample_rate} Hz")
        
        # Audio parameters
        duration = 5  # Record for 5 seconds (reduced from 10)
        
        try:
            # Process audio to get recognized text and matched country
            recognized_text, matched_country = _process_audio_for_speech(
                model, sample_rate, duration
            )
        except Exception as audio_err:
            logging.error(f"Error during audio recording: {str(audio_err)}")
            return jsonify({
                'status': 'error',
                'message': f"Error recording audio: {str(audio_err)}"
            }), 500
        
        # After recording completes, process the results
        return _handle_voice_recognition_result(recognized_text, matched_country)
    
    except ImportError as e:
        missing_module = str(e).split("'")
        if len(missing_module) > 1:
            module_name = missing_module[1]
        else:
            module_name = str(e)
        error_msg = f"Required module not found: {module_name}. Please install it with 'pip install {module_name}'."
        logging.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500
    except Exception as e:
        logging.error(f"Error in voice processing: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f"Error processing voice: {str(e)}"
        }), 500

def _handle_voice_recognition_result(recognized_text, matched_country):
    """
    Handle the result of voice recognition and country matching.
    
    Args:
        recognized_text: The text recognized from speech
        matched_country: The country name matched from the text, if any
        
    Returns:
        flask.Response: JSON response with appropriate status code
    """
    if matched_country:
        try:
            # Use the existing function to update the flag
            success = update_flag_safely(matched_country, force_cleanup=True)
            
            if success == 0:
                return jsonify({
                    'status': 'success',
                    'message': f"Changed flag to {matched_country}",
                    'country': matched_country,
                    'transcribed_text': recognized_text
                }), 200
            else:
                return jsonify({
                    'status': 'partial_success',
                    'message': f"Partially updated flag to {matched_country}, but display may not have updated",
                    'country': matched_country,
                    'transcribed_text': recognized_text
                }), 202
        except Exception as e:
            error_msg = f"Error updating flag: {str(e)}"
            logging.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': error_msg,
                'transcribed_text': recognized_text
            }), 500
    elif recognized_text:
        return jsonify({
            'status': 'not_found',
            'message': f"No country name recognized in: '{recognized_text}'",
            'transcribed_text': recognized_text
        }), 404
    else:
        return jsonify({
            'status': 'timeout',
            'message': "No speech detected during the listening period"
        }), 408