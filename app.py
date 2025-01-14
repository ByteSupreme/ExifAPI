from flask import Flask, request, jsonify
import piexif
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    image_file = request.files['image']
    
    # Save the file temporarily
    temp_file_path = f"{image_file.filename}"
    image_file.save(temp_file_path)
    
    try:
        # Load EXIF data
        exif_dict = piexif.load(temp_file_path)
        exif_data = {}
        
        # Extract EXIF data
        for ifd in ("0th", "Exif", "GPS", "1st"):
            for tag in exif_dict[ifd]:
                tag_name = piexif.TAGS[ifd][tag]["name"]
                tag_value = exif_dict[ifd][tag]
                
                # Decode bytes to string if necessary
                if isinstance(tag_value, bytes):
                    tag_value = tag_value.decode(errors="ignore")
                
                exif_data[tag_name] = tag_value
        
        # Remove the temporary file
        #os.remove(temp_file_path)
        
        return jsonify(exif_data)
    
    except Exception as e:
        # Ensure the temporary file is deleted in case of an exception
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)