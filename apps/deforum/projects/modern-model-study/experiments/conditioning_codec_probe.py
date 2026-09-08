"""Seven VAE round trips with no diffusion, warp or intermediate PNG encoding."""
import conditioning as c

if __name__ == '__main__':
    n=c.a.workflows.node
    g={'3':n('VAELoader',vae_name='flux2-vae.safetensors'),
       '20':n('LoadImage',image='anchor.png')}
    pixels=['20',0]
    for i in range(7):
        enc,dec=str(30+i*2),str(31+i*2)
        g[enc]=n('VAEEncode',pixels=pixels,vae=['3',0])
        g[dec]=n('VAEDecode',samples=[enc,0],vae=['3',0])
        pixels=[dec,0]
    g['11']=n('SaveImage',images=pixels,filename_prefix='conditioning/codec')
    folder=c.run('klein-codec-seven',g,c.OUT/'klein/opening.png')
    c.a.copy(folder/'frames/0000.png',c.OUT/'klein/codec-seven.png')
