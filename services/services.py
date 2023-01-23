from MSGNet import MSGnet
from torch.autograd import Variable
import torch
from io import BytesIO

style_model = MSGnet.Net(ngf=128)
model_dict = torch.load('MSGNet/21styles.model')
model_dict_clone = model_dict.copy()
for key, value in model_dict_clone.items():
    if key.endswith(('running_mean', 'running_var')):
        del model_dict[key]
style_model.load_state_dict(model_dict, False)


def stylize_image(sample, style):
    content_image = MSGnet.tensor_load_rgbimage(sample, size=512,
                                         keep_asp=True).unsqueeze(0)
    style = MSGnet.tensor_load_rgbimage(style, size=512).unsqueeze(0)
    style = MSGnet.preprocess_batch(style)
    style_v = Variable(style)
    content_image = Variable(MSGnet.preprocess_batch(content_image))
    style_model.setTarget(style_v)
    output = style_model(content_image)
    out_image = MSGnet.tensor_get_image(output.data[0], False)
    bio = BytesIO()
    # bio.name('stylized.jpeg')
    out_image.save(bio, 'JPEG')
    bio.seek(0)
    return bio
