import torch
import torch.nn.functional as F

from midi_to_piano_roll import midi_to_piano_roll

torch.manual_seed(10)

# output = torch.rand((88, 1000))
# target = torch.rand((88, 1010))

# pred = torch.tensor( [[0, 0.8, 0, 0, 0, 0.3, 0, 0.1, 0.2, 0],
#                       [0.2, 0, 0.9, 0, 0.2, 0, 0, 0, 0, 0.8],
#                       [0, 0, 0.3, 0, 0.3, 0, 0.3, 0, 0.3, 0.3],
#                       [0, 0.8, 0, 0, 0, 0.3, 0, 0.1, 0.2, 0],
#                       [0.2, 0, 0.9, 0, 0.2, 0, 0, 0, 0, 0.8],
#                       [0, 0, 0.3, 0, 0.3, 0, 0.3, 0, 0.3, 0.3]], requires_grad=True, dtype=torch.float32)

pred = torch.tensor( [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], requires_grad=True, dtype=torch.float32).T.unsqueeze(0)

pred = pred.repeat(2, 1, 1)

# target = torch.tensor( [[0, 0, 0.6, 0, 0, 0, 0.3, 0, 0, 0.8],
#                         [0, 0, 0, 1, 0.2, 0, 0.1, 0.1, 0.8, 0],
#                         [0, 0, 0, 0, 0, 0.3, 0.3, 0, 0.3, 0],
#                         [0, 0, 0.6, 0, 0, 0, 0.3, 0, 0, 0.8],
#                         [0, 0, 0, 1, 0.2, 0, 0.1, 0.1, 0.8, 0],
#                         [0, 0, 0, 0, 0, 0.3, 0.3, 0, 0.3, 0]], dtype=torch.float32)

target = torch.tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=torch.float32).T.unsqueeze(0)

target = target.repeat(2, 1, 1)

def blur_loss(pred, target, device="cpu", save_memory=True):
    # pad tensors to same length
    if pred.shape[1] > target.shape[1]:
        target = F.pad(target, (0, 0, 0, pred.shape[1] - target.shape[1]))
    elif target.shape[1] > pred.shape[1]:
        pred = F.pad(pred, (0, 0, 0, target.shape[1] - pred.shape[1]))

    # blur predicted output to account for small discrepancies in prediction
    blur_level = 1
    blur_kernel = torch.ones(blur_level * 2 + 1, blur_level * 2 + 1).to(device)

    blur_pred = F.conv2d(pred.unsqueeze(1), blur_kernel.unsqueeze(0).unsqueeze(0))
    blur_pred[blur_pred != 0] = 1
    blur_pred = F.pad(blur_pred, (blur_level, blur_level, blur_level, blur_level))

    # stack outputs to form a 4D tensor (batch, dummy axis, time axis, frequency axis)
    bale = blur_pred.repeat(1, target.shape[2], 1, 1)

    # if device=="cuda":
    #     torch.cuda.empty_cache()
        
    if save_memory:
        # apply elementwise MSE
        bale = bale.to("cpu")
        target_filter = torch.ceil(target.mT.unsqueeze(3)).to("cpu")
        bale = (bale - target_filter) ** 2

        # multiply elementwise along frequency axis to preserve only relevant (timed) notes in each slice
        bale = bale * target_filter

        # diagonal filter across time axis
        diag_filter = torch.eye(target.shape[2]).unsqueeze(1).unsqueeze(0).repeat(target.shape[0], 1, 1, 1).to("cpu")
        bale = bale * diag_filter

        bale = bale.to("cuda")
        target_filter = target_filter.to("cuda")

        loss = torch.sum(bale, dim=(1,2,3)) / torch.sum(target_filter, dim=(1,2,3))
    else:
        # apply elementwise MSE
        target_filter = torch.ceil(target.mT.unsqueeze(3))
        bale = (bale - target_filter) ** 2

        # multiply elementwise along frequency axis to preserve only relevant (timed) notes in each slice
        bale = bale * target_filter

        # diagonal filter across time axis
        diag_filter = torch.eye(target.shape[2]).unsqueeze(1).unsqueeze(0).repeat(target.shape[0], 1, 1, 1)
        bale = bale * diag_filter


        # loss is normalized across number of notes in target

        loss = torch.sum(bale, dim=(1,2,3)) / torch.sum(target_filter, dim=(1,2,3))

    return loss

def mse_loss(pred, target):
    # pad tensors to same length
    if pred.shape[1] > target.shape[1]:
        target = F.pad(target, (0, 0, 0, pred.shape[1] - target.shape[1]))
    elif target.shape[1] > pred.shape[1]:
        pred = F.pad(pred, (0, 0, 0, target.shape[1] - pred.shape[1]))
    
    return torch.sum((pred - target) ** 2, dim=(1,2,3)) / torch.sum(torch.ceil(target), dim=(1,2,3))

def song_loss(pred, target):
    return mse_loss(pred, target) + blur_loss(pred, target)

if __name__ == "__main__":
    print("Ready")
    pred_file_path = 'data/clean_data/0_0_song.midi'     # pred
    pred = midi_to_piano_roll(pred_file_path).unsqueeze(0)
    target_file_path = 'data/clean_data/0_0_cover.midi'     # target
    target = midi_to_piano_roll(target_file_path).unsqueeze(0)
    # pred = torch.zeros_like(target)
    print("Calculating mse loss")
    #mse_loss = mse_loss(pred, target)
    #print("mse:", mse_loss)
    print("Calculating blur loss")
    print(target.shape)
    print(pred.shape)
    blur_loss = blur_loss(pred, target)
    print("blur:", blur_loss)

#print(torch.autograd.grad(loss, pred))