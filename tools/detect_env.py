import sys
import torch
import ctypes.util

def print_header(title):
    print(f"\n=== {title} ===")

def check_torch_cuda():
    print_header("PyTorch CUDA Environment")

    try:
        print("PyTorch Version:", torch.__version__)
        print("CUDA Available:", torch.cuda.is_available())
        print("CUDA Version:", torch.version.cuda)
        print("cuDNN Version:", torch.backends.cudnn.version())
        
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print("GPU Device:", torch.cuda.get_device_name(device))
        else:
            print("WARNING: torch.cuda.is_available() == False")

    except Exception as e:
        print("[ERROR] Torch CUDA check failed:", e)

def check_cuda_dll():
    print_header("CUDA Runtime DLL Path")

    try:
        dll = ctypes.util.find_library("cudart")
        if dll:
            print("CUDA DLL Loaded:", dll)
        else:
            print("CUDA DLL not found via ctypes")
    except Exception as e:
        print("[ERROR] DLL lookup failed:", e)

def check_tensor_ops():
    print_header("Tensor Sanity Check")

    try:
        a = torch.rand(1024, 1024, device="cuda")
        b = torch.rand(1024, 1024, device="cuda")
        c = torch.matmul(a, b)
        print("Tensor matmul passed:", c.shape)
        print("Result checksum (sum):", c.sum().item())
    except Exception as e:
        print("[ERROR] Tensor operation failed:", e)

if __name__ == "__main__":
    print("Rope Runtime Diagnostic Tool")
    check_torch_cuda()
    check_cuda_dll()
    check_tensor_ops()
