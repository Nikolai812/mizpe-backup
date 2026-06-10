from astropy.io import fits
import glob, os

for fits_file in glob.glob("AutoFlat*.fts"):
    try:
        header = fits.getheader(fits_file)

        if header.get("NAXIS2") == 2080:
            new_name = "polar_"+fits_file
            command = "mv "+fits_file+" "+new_name
            print(command)
            os.system(command)

    except Exception as e:
        print(f"Error processing {fits_file}: {e}")
