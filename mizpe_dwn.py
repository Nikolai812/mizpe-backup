import datetime
import re
import os
import paramiko
import subprocess

from polar_renamer import rename_polar_flats


def download_subdirectories_with_rsync(subdirs, remote_base_path, local_base_path, ssh_user, ssh_host):
    """
    Downloads selected remote subdirectories using rsync over SSH.

    Parameters:
        subdirs (list): list of remote subdirectory names to download
        remote_base_path (str): base directory on the remote server
        local_base_path (str): base directory on the local machine to receive files
        ssh_user (str): SSH username
        ssh_host (str): SSH host/IP
    """
    for subdir in subdirs:
        remote_path = f"{ssh_user}@{ssh_host}:{os.path.join(remote_base_path, subdir)}/"
        local_path = os.path.join(local_base_path, subdir)

        print(f"Downloading {remote_path} → {local_path}")
        try:
            subprocess.run(
                ["rsync", "-avz", "-e", "ssh", remote_path, local_path],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error downloading '{subdir}': {e}")



def list_subdirectories(path):
    """
    Returns a list of immediate subdirectory names in the given local path.
    """
    try:
        return [name for name in os.listdir(path)
                if os.path.isdir(os.path.join(path, name))]
    except Exception as e:
        print(f"Error reading local path '{path}': {e}")
        return []

def list_remote_subdirectories(ssh, remote_path):
    """
    Uses an existing paramiko SSH connection to list subdirectories on the remote path.
    Returns a list of subdirectory names.
    """
    try:
        command = f"find '{remote_path}' -mindepth 1 -maxdepth 1 -type d -exec basename {{}} \\;"
        stdin, stdout, stderr = ssh.exec_command(command)
        errors = stderr.read().decode().strip()
        if errors:
            print(f"Remote error: {errors}")
            return []
        all_names = stdout.read().decode().splitlines()
        filtered_names = filter_2025_2028_subdirectories(all_names)
        to_remove = sorted(set(all_names) -  set(filtered_names))
        print(f"filtering out remote subdirs: {to_remove}")
        return filtered_names
    except Exception as e:
        print(f"Error retrieving remote directories: {e}")
        return []



def filter_2025_2028_subdirectories(subdir_list):
    """
    Returns only subdirectory names that start with '2025', '2026', '2027', or '2028'.
    """
    pattern = re.compile(r'^202[5-8]')
    return [name for name in subdir_list if pattern.match(name)]



def filter_2025_only_subdirectories(subdir_list):
    """
    Returns only subdirectory names that start with '2025'.
    """
    pattern = re.compile(r'^2025')
    return [name for name in subdir_list if pattern.match(name)]


def syncronize_directories(local_path, remote_path, ssh_host, ssh_user, ssh_key=None, ssh_password=None):
    """
    Syncronizes subdirectories of local and remote paths.
    Prints remote subdirectories that are not present locally.
    """
    local_subdirs = list_subdirectories(local_path)
    print(f"Local subdirectories in '{local_path}': {local_subdirs}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if ssh_key:
            ssh.connect(ssh_host, username=ssh_user, key_filename=ssh_key)
        else:
            ssh.connect(ssh_host, username=ssh_user, password=ssh_password)

        print(f"Connected to {ssh_host}. Fetching remote subdirectories in '{remote_path}'...")
        remote_subdirs = list_remote_subdirectories(ssh, remote_path)
        print(f"Remote subdirectories in '{remote_path}': {remote_subdirs}")

        # Find subdirectories on remote that are not on local
        missing_locally = sorted(set(remote_subdirs) - set(local_subdirs))
        print("\nPattern(^202[5-8]) matching subdirectories present remotely but missing locally:")
        for subdir in missing_locally:
            print(f" - {subdir}")

        download_subdirectories_with_rsync(missing_locally, remote_path, local_path, ssh_user, ssh_host)

        print("Going to apply polar renaming for the appropriate downloaded files (with NAXIS2==2080 )")
        for subdir in missing_locally:
            subdir_path = str(os.path.join(local_path, subdir))
            print(f"!!! Polar renaming for: {subdir_path}")
            rename_polar_flats(subdir_path)

        print("Polar renaming for missing locally subdirectories completed")
    finally:
        ssh.close()
        print(f"Disconnected from {ssh_host}")

# Example usage
if __name__ == "__main__":
    # Replace these with actual values or load from config
    local_path = "/lustre1/home/HPC_CALC/FACULTY_STORAGE/ASTRONOMICAL_STORAGE/MIZPE_BACKUP_PROJECT/H80backup"
    remote_path = "/home/mizpe-bck/H80backup"
    ssh_host = "132.66.135.11"
    ssh_user = "observer"
    ssh_key = None  # or path to private key
    ssh_password = "your_password_here"  # use only if not using key

    start_time = datetime.datetime.now()
    print(f"Starting synchronization with mizpe: {ssh_host} at {start_time}")

    syncronize_directories(local_path, remote_path, ssh_host, ssh_user, ssh_key, ssh_password)

    end_time = datetime.datetime.now()
    print(f"Synchronization with mizpe ended at {end_time}")
