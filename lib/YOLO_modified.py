from ultralytics import nn
import torch
class CustomConv(nn.modules.Conv):
    def __init__(self, c1, c2, k=1, s=1, p=None, g=1, d=1, act=True):
        super().__init__( c1, c2, k, s, p, g, d, act)
    def forward(self,x):
        x=torch.fft.rfftn(x,s=x.size())#Преобразование входа
        weight_data = self.conv.weight.data
        self.conv.weight.data = torch.fft.rfftn(weight_data,s=weight.data.size())#Преобразование весов
        x=self.conv(x)
        self.conv.weight.data=weight_data
        x=self.bn(x)
        x=self.act(x)
        x=torch.fft.irfftn(x,size(x))
        return x
def conv_replace(model):
    returned_module=torch.nn.Sequential()
    for i,module in enumerate(list(model.model.modules())):
        if isinstance(module,nn.modules.Conv):
                custom_conv = CustomConv(
                c1=module.conv.in_channels,
                c2=module.conv.out_channels,
                k=module.conv.kernel_size[0],
                s=module.conv.stride[0],
                p=module.conv.padding[0] if module.conv.padding else None,
                g=module.conv.groups,
                d=module.conv.dilation[0],
                act=module.act is not None,
            )
                returned_module=torch.nn.Sequential(returned_module,custom_conv)
        else:
                returned_module=torch.nn.Sequential(returned_module,module)
        returned_module=module
    return model