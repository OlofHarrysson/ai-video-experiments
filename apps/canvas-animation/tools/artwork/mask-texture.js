/* Rasterize vector controls independently of the artwork they affect. */
window.ArtworkMasks = {
  render(data, {colors, width = data.width, height = data.height, feather = 3}) {
    if (!(width > 0 && height > 0 && data.coordinateScale > 0 && feather >= 0)) {
      throw Error('Invalid mask dimensions, coordinate scale or feather');
    }
    const canvas = Object.assign(document.createElement('canvas'), {width, height});
    const context = canvas.getContext('2d');
    context.fillStyle = 'black';
    context.fillRect(0, 0, width, height);
    context.scale(width / data.width / data.coordinateScale, height / data.height / data.coordinateScale);
    for (const [layer, paths] of Object.entries(data.layers)) {
      if (!Object.hasOwn(colors, layer)) throw Error('No control channel for mask: ' + layer);
      context.fillStyle = colors[layer];
      for (const item of paths) {
        const match = (item.transform || '').match(/^translate\(\s*([-\d.eE+]+)[,\s]+([-\d.eE+]+)\s*\)$/);
        if (item.transform && !match) throw Error('Mask transform must be translation');
        context.save();
        if (match) context.translate(Number(match[1]), Number(match[2]));
        context.fill(new Path2D(item.d));
        context.restore();
      }
    }
    if (!feather) return canvas;
    const soft = Object.assign(document.createElement('canvas'), {width, height});
    const output = soft.getContext('2d');
    output.fillStyle = 'black';
    output.fillRect(0, 0, width, height);
    output.filter = `blur(${feather * width / data.width}px)`;
    output.drawImage(canvas, 0, 0);
    return soft;
  }
};
