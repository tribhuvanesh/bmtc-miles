import tempfile
import subprocess
import os
import re
import sys

def convert_price_to_score(price):
    '''
    Temporarily gives 1 point per Rs. 5, with a minumum of 1 point
    '''
    return price//5 if price >=5 else 1.0

def convert_img_to_price(path):
    '''
    Takes an img path as argument and returns a list of tuples (TicketPrice, Score)
    If path is invalid, throws an OSError
    '''
    # Use tesseract to write the OCR'd content to a tempfile
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tname = tfile.name
    tfile.close()
    try:
        subprocess.call(["tesseract", path, tname])

        # Extract the required information from the tempfile
        # Tesseract appends the filename with a .txt
        _tname = tname + '.txt'
        tfile = open(_tname)

        # Search for a floating point number
        matches = re.findall(r"\d+\.\d+", tfile.read())
        return map(lambda x : (x, convert_price_to_score(x)), map(float, matches))
    finally:
        # Discard the tempfile
        tfile.close()
        os.remove(tname)
        os.remove(_tname)


def main():
    assert len(sys.argv) == 2, "Usage: python ticketlib.py <img-path>"
    print convert_img_to_price(sys.argv[1])


if __name__ == '__main__':
    main()
