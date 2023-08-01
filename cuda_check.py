import torch

print("Cuda availability:", torch.cuda.is_available())
print("Cuda device count:", torch.cuda.device_count())

if torch.cuda.is_available():
    print("Cuda device name:", torch.cuda.get_device_name(0))