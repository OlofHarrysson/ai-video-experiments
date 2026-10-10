/* GMESH001: opaque RGB geometry. DecompressionStream is required; failures are explicit. */
window.ArtworkMesh={
 async unpack(base64){
  const compressed=Uint8Array.from(atob(base64),c=>c.charCodeAt(0));
  const stream=new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'));
  const buffer=await new Response(stream).arrayBuffer(),view=new DataView(buffer);
  if(new TextDecoder().decode(new Uint8Array(buffer,0,8))!=='GMESH001')throw Error('Unsupported mesh format');
  const width=view.getUint32(8,true),height=view.getUint32(12,true),vertices=view.getUint32(16,true),indices=view.getUint32(20,true);
  const indexOffset=Math.ceil((24+vertices*7)/4)*4;
  if(!width||!height||vertices<4||indices%3||indexOffset+indices*4!==buffer.byteLength)throw Error('Invalid mesh dimensions or buffer size');
  const positions=new Uint16Array(buffer,24,vertices*2),colors=new Uint8Array(buffer,24+vertices*4,vertices*3),triangles=new Uint32Array(buffer,indexOffset,indices);
  for(const index of triangles)if(index>=vertices)throw Error('Mesh index exceeds vertex count');
  return {width,height,positions,colors,triangles};
 }
};
