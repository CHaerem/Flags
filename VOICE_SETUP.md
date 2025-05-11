# Voice Recognition Setup for FlagPi

If you need to set up voice recognition, follow these steps:

1. SSH into your FlagPi or access a terminal on it

2. Navigate to the Flags directory:
   ```
   cd ~/Flags
   ```

3. Make sure the download script is executable:
   ```
   chmod +x scripts/download_vosk_model.sh
   ```

4. Run the script to download and install the Vosk model:
   ```
   ./scripts/download_vosk_model.sh
   ```
   
   This will:
   - Download the `vosk-model-en-us-0.22` model (approximately 1.8GB)
   - Extract it to the models directory
   - Clean up the zip file to save space

5. After installation completes, restart the Flask service:
   ```
   sudo systemctl restart flag-api.service
   ```

## Troubleshooting

If you encounter issues with sample rates, the application is configured to use these rates in order of preference:
1. 44100 Hz
2. 48000 Hz
3. 16000 Hz
4. 8000 Hz

The application will automatically detect which sample rates are supported by your audio device.

## Testing Voice Recognition

You can test if voice recognition is working with:
```
curl -X POST http://FlagPi.local/voice-listen
```

Watch the logs for troubleshooting:
```
sudo journalctl -u flag-api.service -f
```
