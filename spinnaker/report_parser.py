import re
import csv
import pdb
import argparse

# Initialize a list to store the parsed data
parsed_data = []

def parse_args():

    parser = argparse.ArgumentParser(description='Automatic Coordinate Location')

    parser.add_argument('-n', '--net', type=str, help="Net name: convolutioner|mapper|projector", default="convolutioner")

    return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()
    net = args.net 

    # Define the path to your .rpt file
    file_path = f'reports/{net}/run_1/placement_by_core_using_graph.rpt'

    # Open the file and read it line by line
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Regular expression patterns to capture the relevant data
    chip_pattern = re.compile(r"\*\*\*\* Chip: \((\d+), (\d+)\)")  # Capture chip_id and board_id
    processor_pattern = re.compile(r"\s*Processor (\d+):")  # Capture processor_id
    vertex_pattern = re.compile(r"\s*Vertex: '([^']+)'")  # Capture vertex name
    sdram_pattern = re.compile(r"SDRAM required: (\d+)")  # Capture SDRAM value

    # Initialize variables to keep track of chip and processor data
    chip_id = board_id = None
    processor_id = 1  # Processor IDs start from 1


    # Loop through each line in the file
    for line in lines:
        
        # pdb.set_trace()
        chip_match = chip_pattern.match(line)
        if chip_match:
            # If a chip is found, extract the chip coordinates
            chip_id = int(chip_match.group(1))
            board_id = int(chip_match.group(2))
            # if net == 'convolutioner':
            #     chip_id = int(chip_match.group(1))
            #     board_id = int(chip_match.group(2))
            # else:
            #     chip_id = int(chip_match.group(1))+7*int(chip_match.group(2))
            #     board_id = 0


            continue
        
        processor_match = processor_pattern.match(line)
        if processor_match:
            # If a processor is found, capture the processor id
            processor_id = int(processor_match.group(1))
        
        vertex_match = vertex_pattern.search(line)
        if vertex_match:
            # If a vertex is found, capture the vertex name
            vertex = vertex_match.group(1)
            continue
        
        sdram_match = sdram_pattern.search(line)
        if sdram_match:
            # If SDRAM is found, capture the SDRAM value
            sdram = int(sdram_match.group(1))
            
            # Append the parsed data to the list
            parsed_data.append([board_id, chip_id, processor_id, vertex, sdram])

    # Define the path for the output CSV file
    csv_file_path = f'results/data/parsed_{net}.csv'

    # Write the parsed data into a CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        writer.writerow(['board_id', 'chip_id', 'processor_id', 'vertex', 'SDRAM'])
        # Write the data rows
        writer.writerows(parsed_data)

    print(f"Data successfully parsed and saved to {csv_file_path}")
