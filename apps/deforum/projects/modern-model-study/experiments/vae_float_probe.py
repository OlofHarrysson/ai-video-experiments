"""Keep float IMAGE tensors between VAE cycles; save only diagnostic snapshots."""
import json
import repaint_diagnosis as d

CYCLES=[1,4,11,24]

def graph():
    n=d.a.workflows.node
    g={'3':n('VAELoader',vae_name='qwen_image_vae.safetensors'),'20':n('LoadImage',image='anchor.png')}
    previous=['20',0];snapshots=[]
    for i in range(1,25):
        enc,dec=str(100+i*2),str(101+i*2)
        g[enc]=n('VAEEncode',pixels=previous,vae=['3',0]);g[dec]=n('VAEDecode',samples=[enc,0],vae=['3',0]);previous=[dec,0]
        if i in CYCLES:snapshots.append(previous)
    batch=snapshots[0]
    for i,snapshot in enumerate(snapshots[1:]):
        key=str(300+i);g[key]=n('ImageBatch',image1=batch,image2=snapshot);batch=[key,0]
    g['11']=n('SaveImage',images=batch,filename_prefix='repaint-diagnosis/vae-float')
    return g


def run():
    name='repaint-diagnosis-v001-vae-float';g=graph()
    matches=list((d.a.PROJECT/'runs').glob('*-'+name+'-4f'))
    if matches:
        assert len(matches)==1;folder=matches[0]
        assert json.loads((folder/'workflow.api.json').read_text())==g
        assert d.a.sha(folder/'anchor.png')==d.a.sha(d.SOURCE)
        d.a.transport.collect(folder)
    else:
        folder=d.a.transport.submit(d.a.PROJECT,name,g,4,source=d.SOURCE,
            lineage={'study':'repaint-diagnosis-v001','case':'vae-float','cycles':CYCLES,'motion':'none',
                'feedback':'VAEDecode float IMAGE wired directly to next VAEEncode; no intermediate PNG input'})
    root=d.OUT/'vae-float';d.a.copy(d.SOURCE,root/'anchors/0000.png')
    for j,i in enumerate(CYCLES):d.a.copy(folder/f'frames/{j:04d}.png',root/f'anchors/{i:04d}.png')
    d.a.save(root/'manifest.json',{'cycles':CYCLES,'run':str(folder.relative_to(d.a.PROJECT)),'graph':g,
        'source_sha256':d.a.sha(d.SOURCE),'outputs':{i:d.a.sha(root/f'anchors/{i:04d}.png') for i in CYCLES}})
    print('Float VAE probe complete',flush=True)


if __name__=='__main__':run()
