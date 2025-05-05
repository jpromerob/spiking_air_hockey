import os

def process_aedat4_files(folder_path):
    # List all .aedat4 files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith('.aedat4')]
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        print(f"Found file: {file}")
        # os.system(f'/opt/aestream/build/src/aestream output udp 172.16.222.30 3030 input file {file} ')

        cmd = ""
        cmd +=f"/opt/aestream/build/src/aestream "
        cmd +=f"resolution 1280 720 undistortion ../calibration/luts/cam_lut_homography_prophesee.csv "
        cmd +=f"input file {file} output udp 172.16.222.30 3030 172.16.223.2 3333"

        os.system(cmd)

        # Ask the user for input
        response = input("Are you happy with this file? (Y/N): ")
        
        if response.strip().upper() == 'N':
            try:
                os.remove(file_path)
                print(f"File '{file}' has been removed.")
            except Exception as e:
                print(f"Could not remove file '{file}': {e}")
        else:
            print(f"File '{file}' retained.")

# Usage example
folder_path = './'  # Replace with your target folder path
process_aedat4_files(folder_path)
