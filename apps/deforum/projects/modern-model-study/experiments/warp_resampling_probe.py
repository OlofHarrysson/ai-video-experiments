"""A local Lanczos resampling control; does not change the animation runner."""
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import repaint_diagnosis as d
from repaint_diagnosis_review import metrics

root=d.OUT/'warp-lanczos'
original=np.asarray(Image.open(d.SOURCE).convert('RGB'));current=original.copy()
for i in range(12):
    if i:
        coords=d.a.motion.coordinates((i-1)*3,i*3,width=d.c.WIDTH,height=d.c.HEIGHT)
        current=cv2.remap(current,coords,None,cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REFLECT_101)
    d.a.image(root/f'anchors/{i:04d}.png',current)
reference=np.asarray(Image.open(d.OUT/'warp-once/anchors/0011.png').convert('RGB'))
d.a.save(root/'diagnostics.json',{'method':'OpenCV INTER_LANCZOS4, eleven repeated warps, uint8 RGB',
    'interpretation':'local resampling control only; repaint interaction and ringing require inspection',**metrics(current,reference)})
canvas=Image.new('RGB',(1536,552),'#15191d');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',24)
for j,(case,label) in enumerate([('warp-repeated','Current bilinear: eleven warps'),('warp-lanczos','Lanczos: same eleven warps')]):
    im=Image.open(d.OUT/f'{case}/anchors/0011.png').crop((240,100,1008,612));canvas.paste(im,(j*768,40));draw.text((j*768+12,8),label,font=font,fill='white')
d.a.image(root/'detail.png',np.asarray(canvas))
print('Lanczos control saved; animation pipeline unchanged')
