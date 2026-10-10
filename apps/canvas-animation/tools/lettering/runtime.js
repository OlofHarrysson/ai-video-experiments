/* Source-coordinate geometry; the caller owns placement, material and motion. */
window.Lettering = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  const union = parts => {
    const x = Math.min(...parts.map(p => p.bounds[0])), y = Math.min(...parts.map(p => p.bounds[1]));
    return [x, y, Math.max(...parts.map(p => p.bounds[0] + p.bounds[2])) - x,
      Math.max(...parts.map(p => p.bounds[1] + p.bounds[3])) - y];
  };
  function prepare(asset) {
    const svg = document.createElementNS(NS, 'svg');
    svg.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none';
    document.body.append(svg);
    try {
      const parts = asset.parts.map(part => {
        const el = document.createElementNS(NS, 'path');
        el.setAttribute('d', part.d); if (part.transform) el.setAttribute('transform', part.transform);
        svg.append(el);
        const m = el.transform.baseVal.consolidate()?.matrix || new DOMMatrix();
        if (m.a !== 1 || m.b !== 0 || m.c !== 0 || m.d !== 1) throw Error('Only translated VTracer paths supported');
        const box = el.getBBox(), path = new Path2D();
        path.addPath(new Path2D(part.d), m);
        return {...part, bounds:[box.x + m.e, box.y + m.f, box.width, box.height], path};
      });
      if (!parts.length || !asset.groups.length) throw Error('Asset requires paths and groups');
      if (new Set(asset.groups.map(g=>g.id)).size !== asset.groups.length) throw Error('Duplicate group ID');
      const assignments = new Map(parts.map(p => [p.id, []]));
      const groups = asset.groups.map(group => {
        if (Boolean(group.region) === Boolean(group.parts)) throw Error('Choose region or explicit parts');
        const selected = group.parts ? group.parts.map(id => {
          const part = parts.find(p=>p.id===id); if(!part) throw Error(`Unknown part ${id}`); return part;
        }) : parts.filter(part => {
          const [x,y,w,h] = part.bounds, [l,t,r,b] = group.region;
          return x>=l*asset.width-1 && y>=t*asset.height-1 && x+w<=r*asset.width+1 && y+h<=b*asset.height+1;
        });
        if (!selected.length) throw Error(`Empty group ${asset.id}/${group.id}`);
        selected.forEach(p=>assignments.get(p.id).push(group.id));
        const bounds = union(selected), pivot = group.pivot || [.5,.5], path = new Path2D();
        if(pivot.length!==2 || pivot.some(n=>!Number.isFinite(n)||n<0||n>1)) throw Error('Pivot must be normalized 0..1');
        selected.forEach(p=>path.addPath(p.path));
        const {region,...metadata}=group;
        return {...metadata, sourceRegion:region, parts:selected.map(p=>p.id), bounds, pivot,
          pivotPoint:[bounds[0]+bounds[2]*pivot[0], bounds[1]+bounds[3]*pivot[1]], path};
      });
      for(const [id, memberships] of assignments) if(memberships.length!==1)
        throw Error(`${asset.id}/${id} belongs to ${memberships.length} groups; use explicit path IDs for overlapping word bounds`);
      const path = new Path2D(); parts.forEach(p=>path.addPath(p.path));
      return {...asset, parts, groups, bounds:union(parts), path};
    } finally { svg.remove(); }
  }
  function serializable(asset) {
    const {path,...a}=asset;
    return {...a, parts:a.parts.map(({path,...p})=>p), groups:a.groups.map(({path,...g})=>g)};
  }
  return {prepare, serializable};
})();
