import os
import subprocess
import sys

def resolve_cuda_version():
    cuda_path = os.environ.get("CUDA_PATH", "").lower().replace('"', '')

    if "v12.4" in cuda_path:
        return "cu124"
    elif "v12.8" in cuda_path:
        return "cu128"
    else:
        print("[ERROR] Unable to detect CUDA version from CUDA_PATH")
        print("  CUDA_PATH =", cuda_path)
        print("  Expected path to include 'v12.4' or 'v12.8'")
        sys.exit(1)

def install_requirements(cuda_version):
    req_file = f"requirements_{cuda_version}.txt"
    if not os.path.isfile(req_file):
        print(f"[ERROR] Requirements file not found: {req_file}")
        sys.exit(1)
    print(f"[INFO] Installing: {req_file}")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "-r", req_file, "--default-timeout", "100"
    ])

def post_install_diagnostics():
    print("\n=== Diagnostics ===")
    try:
        import torch
        import ctypes.util

        print("CUDA:   ", torch.version.cuda)
        print("cuDNN:  ", torch.backends.cudnn.version())
        print("Device: ", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")
        print("Is Available:", torch.cuda.is_available())

        cudart = ctypes.util.find_library("cudart")
        print("DLL loaded from:", cudart if cudart else "Not found")

        # Tensor sanity check
        if torch.cuda.is_available():
            a = torch.rand(512, 512, device="cuda")
            b = torch.rand(512, 512, device="cuda")
            c = torch.matmul(a, b)
            print("Tensor check passed: matmul shape", c.shape)
            print("Tensor checksum:", c.sum().item())
        else:
            print("Tensor check skipped: CUDA unavailable")

    except Exception as e:
        print("[ERROR] Diagnostics failed:", str(e))

if __name__ == "__main__":
    print("[ROPE] Update started")
    version = resolve_cuda_version()
    install_requirements(version)
    post_install_diagnostics()
    print("[ROPE] Update completed successfully")