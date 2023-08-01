'''
Model Architecture: Variational Transformer

Input: Song Midi -> Song Piano Roll

Encoder 

Transformer -> Music Transformer

Decoder

Label: Cover Midi -> Cover Piano roll

'''
import torch
import torch.nn as nn
import math
import numpy as np
import torch.nn.functional as F

class DenseBlock(nn.Module):
    def __init__(self, input_size, depth=5, in_channels=64):
        super(DenseBlock, self).__init__()
        self.depth = depth
        self.in_channels = in_channels
        self.pad = nn.ConstantPad2d((1, 1, 1, 0), value=0.)
        self.twidth = 2
        self.kernel_size = (self.twidth, 3)

        # print("In-channels: ",self.in_channels)
        for i in range(self.depth):
            dil = 2 ** i
            pad_length = self.twidth + (dil - 1) * (self.twidth - 1) - 1
            setattr(self, 'pad{}'.format(i + 1), nn.ConstantPad2d((1, 1, pad_length, 0), value=0.))
            setattr(self, 'conv{}'.format(i + 1),
                    nn.Conv2d(self.in_channels, self.in_channels, kernel_size=self.kernel_size,
                              dilation=(dil, 1)))
            setattr(self, 'norm{}'.format(i + 1), nn.LayerNorm(input_size))
            setattr(self, 'prelu{}'.format(i + 1), nn.PReLU())

    def forward(self, x):
        skip = x
        for i in range(self.depth):
            ## print("Conv in-channels: ", getattr(self, 'conv{}'.format(i + 1)).in_channels)
            # print("New skip dimension: ", skip.shape)
            out = getattr(self, 'pad{}'.format(i + 1))(skip)
            out = getattr(self, 'conv{}'.format(i + 1))(out)
            out = getattr(self, 'norm{}'.format(i + 1))(out)
            out = getattr(self, 'prelu{}'.format(i + 1))(out)
            #skip = torch.cat([out, skip], dim=1)
            # print("Finished Iteration ", i)
            ## print("New skip dimension: ", skip.shape)
        return out



class Encoder(nn.Module):
    def __init__(self, width, batch_size):
        super(Encoder, self).__init__()

        self.in_channels = batch_size
        self.out_channels = 1
        self.kernel_size = (2, 3)
        # self.elu = nn.SELU(inplace=True)
        self.pad = nn.ConstantPad2d((1, 1, 1, 0), value=0.)
        self.pad1 = nn.ConstantPad2d((1, 1, 0, 0), value=0.)
        self.width = width

        self.inp_conv = nn.Conv2d(in_channels=self.in_channels, out_channels=self.width, kernel_size=5)  # [b, 64, nframes, 512]
        self.inp_norm = nn.LayerNorm(124)
        self.inp_prelu = nn.PReLU()

        self.enc_dense1 = DenseBlock(124, 4, self.width)
        self.enc_conv1 = nn.Conv2d(in_channels=self.width, out_channels=self.width, kernel_size=3, stride=3)  # [b, 64, nframes, 256]
        self.enc_norm1 = nn.LayerNorm(42)
        self.enc_prelu1 = nn.PReLU()
    
    def forward(self, x):
        # print("Beginning forward with dimension ", x.shape)
        x = self.inp_conv(x)

        # print("Done 1 with final dimension ", x.shape)
        x = self.inp_norm(x)
        # print("Done 2")
        x = self.inp_prelu(x)
        # print("Done 3")

        x = self.enc_dense1(x) 
        # print("Done 4 with final dimension ", x.shape)
        
        x = self.pad1(x)
        # print("Done 5")
        x = self.enc_conv1(x)
        # print("Done 6 with final dimension ", x.shape)
        x = self.enc_norm1(x)
        # print("Done 7")
        x = self.enc_prelu1(x)
        # print("Done Encoder")

        return x

class Decoder(nn.Module):
    def __init__(self, width, batch_size):
        super(Decoder, self).__init__()
        
        self.width = width

        self.dec_prelu1 = nn.PReLU()
        self.dec_norm1 = nn.LayerNorm(42)
        self.dec_conv1 = nn.ConvTranspose2d(in_channels=self.width, out_channels=self.width, kernel_size=3, stride=3)

        self.dec_dense1 = DenseBlock(124, 4, self.width)

        self.dec_prelu2 = nn.PReLU()
        self.dec_norm2 = nn.LayerNorm(124)
        self.dec_conv2 = nn.ConvTranspose2d(in_channels=self.width, out_channels=batch_size, kernel_size=5)

        self.pad = nn.ConstantPad2d((1, 1, 1, 0), value=0.)
        self.pad1 = nn.ConstantPad2d((1, 1, 0, 0), value=0.)
    
    def forward(self, x):
        # print("Beginning decoder forward with dimension ", x.shape)

        x = self.dec_prelu1(x)
        # print("Done 1 with final dimension ", x.shape)
        x = self.dec_norm1(x)
        # print("Done 2")
        x = self.dec_conv1(x)
        # print("Done 3 with final dimension ", x.shape)
        x= x[..., :124]
        x = self.dec_dense1(x)
        # print("Done 4 with final dimension ", x.shape)

        #x = self.pad1(x)
        # print("Done 5")
        x = self.dec_norm2(x)
        # print("Done 6")
        x = self.dec_conv2(x)
        # print("Done 7 with final dimension ", x.shape)
        x= x[..., :128]
        x = self.dec_prelu2(x)
        # print("Done Decoder")
        return x

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_seq_len=10000):
        super(PositionalEncoding, self).__init__()
        #Note currently max_seq_len is set to 18274, make sure that this is set to the input time-step number after encoder
        self.encoding = torch.zeros(max_seq_len, d_model)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model))
        self.encoding[:, 0::2] = torch.sin(position * div_term)
        self.encoding[:, 1::2] = torch.cos(position * div_term)
        self.encoding = self.encoding.unsqueeze(0)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.encoding = self.encoding.to(device)


    def forward(self, x):
        # Add positional encoding to input embeddings
        # print(self.encoding.shape)
        return x + self.encoding[:, :x.size(1)].detach()
    
class MusicTransformer(nn.Module):
    def __init__(self):
        super(MusicTransformer, self).__init__()
        self.transformer = nn.Transformer(d_model = 42,nhead=2, num_encoder_layers=3,
                                            num_decoder_layers=3, dim_feedforward=3,
                                            dropout=0.15)
        
    def forward(self, x, mask=None):
        self.positional_encoding = PositionalEncoding(42,x.shape[1])
        x = self.positional_encoding(x)
        out = self.transformer(x, x)

        return out

class Net(nn.Module):
    def __init__(self, width, batch_size) -> None:
        super(Net, self).__init__()

        self.encoder = Encoder(width=width, batch_size= batch_size)
        self.music_transfomer = MusicTransformer()
        self.decoder = Decoder(width=width, batch_size=batch_size)
    
    def forward(self, x):
        x = self.encoder(x)
        # print("Encoder Final Dimension", x.shape)
        x = self.music_transfomer(x)
        # print("Transformer Final Dimension", x.shape)
        x = self.decoder(x)
        x = F.softmax(x, dim = 1)
        return x