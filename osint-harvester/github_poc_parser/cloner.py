import os
import shutil
import git
    
import stat

def on_rm_error(func, path, exc_info):
    # Change file to writable and retry deletion
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(url, dest_dir):
    try:
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir, onerror=on_rm_error)
        git.Repo.clone_from(url, dest_dir)
        return True
    except Exception as e:
        print(f"[ERROR] failed to clone {url} : {e}")
        return False
