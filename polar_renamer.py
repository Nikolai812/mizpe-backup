from pathlib import Path
from astropy.io import fits


def rename_polar_flats(directory: str = ".") -> None:
    """
    Rename AutoFlat*.fts files whose NAXIS2 header keyword equals 2080
    by prepending 'polar_' to the filename.

    The operation is idempotent: files already starting with 'polar_'
    are skipped.
    """
    have_polar = 0
    to_rename=0

    for fits_file in Path(directory).glob("*AutoFlat*.fts"):
        try:
            # Idempotence check
            if fits_file.name.startswith("polar_"):
                have_polar += 1
                continue

            header = fits.getheader(fits_file)

            if header.get("NAXIS2") == 2080:
                new_name = fits_file.with_name(f"polar_{fits_file.name}")

                print(f"Renaming: {fits_file} -> {new_name}")
                to_rename += 1
                fits_file.rename(new_name)

        except Exception as e:
            print(f"Error processing {fits_file}: {e}")

    print(f"Already renamed: {have_polar} files, \nto rename {to_rename} files")

def rename_polar_flats_in_subdirs(root: str = ".", mask: str = "") -> None:
    """
    Apply rename_polar_flats() to subdirectories of root.

    Parameters
    ----------
    root : str
        Root directory.

    mask : str
        Glob mask for subdirectories.
        Examples:
            ""          -> all subdirectories
            "2026*"     -> directories beginning with 2026
            "*h80"      -> directories ending with h80
            "202606*"   -> June 2026 directories
    """
    root_path = Path(root)

    if mask:
        dirs = [p for p in root_path.glob(mask) if p.is_dir()]
    else:
        dirs = [p for p in root_path.iterdir() if p.is_dir()]

    for subdir in sorted(dirs):
        print(f"\nProcessing directory: {subdir}")
        rename_polar_flats(str(subdir))



def main():
    #rename_polar_flats("./20260613h80")
    rename_polar_flats_in_subdirs(
        root=".",
        mask="202606*"
    )


if __name__ == "__main__":
    main()