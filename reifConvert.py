import argparse
import sys
import os
import time
import binascii
from math import ceil, sqrt
from PIL import Image
from datetime import datetime

global output

def now():
    return datetime.now()

def rgb_to_ansi(r, g, b):
    # Map each RGB component to the closest value from the 216-color cube
    r = round(r / 255 * 5)
    g = round(g / 255 * 5)
    b = round(b / 255 * 5)
    # Convert cube coordinates to ANSI color code
    code = 16 + (r * 36) + (g * 6) + b
    return f"\u001b[38;5;{code}m"

def encode(input_filename, output_filename):
    startTime = time.time()
    # Read in the input file as binary data
    with open(input_filename, "rb") as f:
        data = f.read()

    # Convert each byte to an 8-bit binary string and concatenate them
    binary_data = "".join([format(byte, "08b") for byte in data])
    if output:
        print("binary_data " + binary_data)

    # Pad the binary data with zeros so its length is a multiple of 24 bits
    padding_length = 24 - len(binary_data) % 24
    if output:
        binary_data += "0" * padding_length

    # Split the binary data into groups of 24 bits, convert each group to a hex string, and concatenate them
    hex_data = "".join([hex(int(binary_data[i:i+24], 2))[2:].zfill(6)
                       for i in range(0, len(binary_data), 24)])

    # Determine the width and height of the image based on the length of the hex data
    num_pixels = ceil(sqrt(len(hex_data) // 6))
    width = height = num_pixels

    # Create a new image with the calculated dimensions
    img = Image.new("RGB", (width, height), color="black")
    if output:
        print(img)

    # Draw each pixel in the image
    for i in range(0, len(hex_data), 6):
        # Extract the RGB values from the hex color code
        r, g, b = tuple(int(hex_data[i:i+2], 16) for i in range(i, i+6, 2))

        # Calculate the x and y coordinates of the pixel
        x = (i // 6) % width
        y = (i // 6) // width

        # Set the pixel color in the image
        img.putpixel((x, y), (r, g, b))
        if output:
            print(str(i) + " Pixel Color: " + rgb_to_ansi(r, g, b) + f"""∎\n\t Pixel Co-ords: ({x}, {y}) \n Pixel RGB value: \n\t\033[31mr {r}\033[0m, \033[32mg {g}\033[0m, \033[34mb {b}\033[0m""")

    # Save the image to a file
    # print(output_filename)
    output_filename = output_filename.split(".")[0]
    # print(output_filename)
    output_filename += ".bmp"
    # print(output_filename)
    img.save(output_filename)

    endTime = time.time()
    if output:
        print("\033[31m~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\033[0m")
        print(f"File \033[32m{input_filename}\033[0m saved to \033[35m{output_filename}\033[0m")
        print(f"Image size: {width} x {height} with a count of {i} pixels.")
        print(f"File converted in {endTime - startTime}s")

    with open(f"log.csv","a") as log:
        log.write(f""" {input_filename},{output_filename},{width},{height},{endTime - startTime}\n,,,,,rgb({r}\,{g}\,{b})""")
    # Rename to reif
    # os.system(f"move {output_filename}.bmp {output_filename}.reif")

###################################################################################################

def decode(input_filename, output_filename, extension):
    # Open the image and load its pixels
    with Image.open(input_filename) as img:
        pixels = img.load()
        width, height = img.size

        # Iterate over each pixel in the image
        hex_data = ""
        for y in range(height):
            for x in range(width):
                # Convert the pixel color to a html color code
                r, g, b = pixels[x, y]
                color_code = '{:02x}{:02x}{:02x}'.format(r, g, b)

                # Ignore black pixels
                if color_code == "000000":
                    continue

                # Convert the html color code to hexadecimal and append it to the hex data string
                hex_data += color_code

    # Convert the hexadecimal string to binary
    binary_data = binascii.unhexlify(hex_data)
    # Remove control characters
    binary_data = bytes(filter(lambda x: x >= 32, binary_data))

    # Write the cleaned data back to the file
    with open(output_filename + "." + extension, 'wb') as f:
        f.write(binary_data)

    with open(output_filename + "." + extension, 'r+') as f:
        contents = f.read()
        contents = contents.replace("  ", "\n")
        f.write(contents)
    
###################################################################################################

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description="Encode or decode a file with a specified extension")

    # Add the mode argument
    parser.add_argument("mode", choices=[
                        "encode", "decode", "e", "d"], help="The mode to use (encode or decode)")

    # Add the filename argument
    parser.add_argument(
        "filename", help="The name of the file to encode or decode")

    # Add the output argument as a flag
    parser.add_argument("-o", "--output",
                        help="The filepath to use for the output file", default=None)

    # Add the extension argument as a flag
    parser.add_argument("-e", "--extension",
                        help="The extension to use for the output file", default=None)

    # Add the show output argument as a flag
    parser.add_argument("-s", "--show",
                        help="Show the output", default=False)

    # Parse the arguments
    args = parser.parse_args()

    output = args.show
    inputFile = args.filename

    # print("args.output " + args.output)
    if args.output == None:
        print("inputFile.split(\".\")[0] " + inputFile.split(".")[0])
        output_filename = inputFile.split(".")[0]
    else:
        output_filename = args.output

    print(output_filename)
    print("Input File " + inputFile)
    print("Output File " + output_filename + " |")

    # Determine whether to encode or decode the file
    if args.mode[0] == "e":
        encode(inputFile, output_filename)
    elif args.mode[0] == "d":
        if args.extension != None:
            extension = args.extension.split(".")[len(args.extension.split("."))]
        else:
            extension = "txt"
        print("extension " + extension)
        decode(inputFile, output_filename, extension)
    else:
        print("Invalid mode")
